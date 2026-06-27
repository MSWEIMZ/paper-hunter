"""JSONL 索引存储测试"""
import json
import pytest
from pathlib import Path
from paper_hunter.storage import load_index, upsert_paper, get_all_records, get_stats, get_existing_ids


def _make_record(cid="2401.00001", title="Test Paper", year=2024, score=3.0, label="strongly_related"):
    return {
        "canonical_id": cid,
        "title": title,
        "year": year,
        "relevance_score": score,
        "quality_label": label,
        "authors": ["Alice"],
        "abstract": "Test abstract.",
    }


def test_load_empty_index(tmp_path):
    """空目录应该返回空 dict"""
    idx = tmp_path / "index.jsonl"
    assert load_index(idx) == {}


def test_upsert_new_paper(tmp_path):
    """新增论文应该返回 True"""
    idx = tmp_path / "index.jsonl"
    rec = _make_record()
    assert upsert_paper(idx, rec) is True
    assert idx.exists()


def test_upsert_existing_paper(tmp_path):
    """更新已有论文应该返回 False"""
    idx = tmp_path / "index.jsonl"
    rec = _make_record()
    upsert_paper(idx, rec)
    rec["relevance_score"] = 5.0
    assert upsert_paper(idx, rec) is False


def test_upsert_dedup(tmp_path):
    """相同 canonical_id 不应重复"""
    idx = tmp_path / "index.jsonl"
    upsert_paper(idx, _make_record(cid="2401.00001", title="Paper A"))
    upsert_paper(idx, _make_record(cid="2401.00001", title="Paper A Updated"))
    records = load_index(idx)
    assert len(records) == 1
    assert records["2401.00001"]["title"] == "Paper A Updated"


def test_get_all_records_sorted(tmp_path):
    """get_all_records 应该按年份降序、分数降序排列"""
    idx = tmp_path / "index.jsonl"
    upsert_paper(idx, _make_record(cid="2401.00001", year=2023, score=3.0))
    upsert_paper(idx, _make_record(cid="2401.00002", year=2024, score=5.0))
    upsert_paper(idx, _make_record(cid="2401.00003", year=2024, score=2.0))
    records = get_all_records(idx)
    assert len(records) == 3
    assert records[0]["year"] == 2024
    assert records[0]["relevance_score"] == 5.0
    assert records[1]["year"] == 2024
    assert records[1]["relevance_score"] == 2.0
    assert records[2]["year"] == 2023


def test_get_stats(tmp_path):
    """get_stats 应该返回正确的统计"""
    idx = tmp_path / "index.jsonl"
    upsert_paper(idx, _make_record(cid="2401.00001", label="core"))
    upsert_paper(idx, _make_record(cid="2401.00002", label="strongly_related"))
    upsert_paper(idx, _make_record(cid="2401.00003", label="noise"))
    stats = get_stats(idx)
    assert stats["total"] == 3
    assert stats["by_label"]["core"] == 1
    assert stats["by_label"]["strongly_related"] == 1
    assert stats["by_label"]["noise"] == 1


def test_get_existing_ids(tmp_path):
    """get_existing_ids 应该返回所有 ID"""
    idx = tmp_path / "index.jsonl"
    upsert_paper(idx, _make_record(cid="2401.00001"))
    upsert_paper(idx, _make_record(cid="2401.00002"))
    ids = get_existing_ids(idx)
    assert ids == {"2401.00001", "2401.00002"}
