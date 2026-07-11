import json
import pytest

from paper_hunter import cli


def _write_profile(tmp_path):
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    profile = profiles / "test.json"
    profile.write_text(json.dumps({
        "profile_name": "Test",
        "output_dir": "output/test",
        "queries": {"core": ["video"]},
        "notification": {"type": "none"},
    }), encoding="utf-8")
    return profile


def test_run_daily_builds_top_k_from_new_records(tmp_path, monkeypatch):
    profile = _write_profile(tmp_path)

    raw_paper = {
        "arxiv_id": "2601.12345v1",
        "title": "Video Understanding",
        "authors": ["A. Author"],
        "summary": "A video paper.",
        "published": "2026-01-01",
        "categories": ["cs.CV"],
        "source": "arxiv",
    }
    monkeypatch.setattr(cli, "collect_candidates", lambda *_: [("core", "video", raw_paper)])
    monkeypatch.setattr(cli, "compute_score", lambda *_args, **_kwargs: 5.0)
    monkeypatch.setattr(cli, "enhance_record", lambda record: record)
    monkeypatch.setattr(cli, "classify_paper_topics", lambda _record: [])
    monkeypatch.setattr(cli, "generate_readme", lambda *_: "readme")
    monkeypatch.setattr(cli, "generate_topics_markdown", lambda *_: "topics")
    monkeypatch.setattr(cli, "generate_trends_markdown", lambda *_: "trends")
    monkeypatch.setattr(cli, "generate_dashboard_html", lambda *_: "dashboard")

    cli.run_daily(profile)

    top_k = tmp_path / "output" / "test" / "TOP_K.md"
    assert top_k.exists()
    assert "Video Understanding" in top_k.read_text(encoding="utf-8")


def test_run_daily_rejects_categories_outside_allowlist(tmp_path, monkeypatch):
    profile = _write_profile(tmp_path)
    raw_paper = {
        "arxiv_id": "2601.99999",
        "title": "Unrelated NLP Paper",
        "summary": "NLP only.",
        "published": "2026-01-01",
        "categories": ["cs.CL"],
    }
    monkeypatch.setattr(cli, "collect_candidates", lambda *_: [("core", "video", raw_paper)])
    monkeypatch.setattr(cli, "compute_score", lambda *_args, **_kwargs: 5.0)
    monkeypatch.setattr(cli, "generate_readme", lambda *_: "readme")
    monkeypatch.setattr(cli, "generate_topics_markdown", lambda *_: "topics")
    monkeypatch.setattr(cli, "generate_trends_markdown", lambda *_: "trends")
    monkeypatch.setattr(cli, "generate_dashboard_html", lambda *_: "dashboard")

    cli.run_daily(profile)

    assert not (tmp_path / "output" / "test" / "index.jsonl").exists()


def test_run_daily_propagates_collection_failure(tmp_path, monkeypatch):
    profile = _write_profile(tmp_path)
    monkeypatch.setattr(cli, "collect_candidates", lambda *_: (_ for _ in ()).throw(OSError("API down")))
    monkeypatch.setattr(cli, "send_notification", lambda *_args, **_kwargs: False)

    with pytest.raises(RuntimeError, match="搜索失败"):
        cli.run_daily(profile)
