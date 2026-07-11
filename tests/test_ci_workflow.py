from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "daily_search.yml"


def test_daily_workflow_configures_src_layout():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "PYTHONPATH:" in text
    assert "${{ github.workspace }}/src" in text


def test_daily_workflow_does_not_hide_search_failures():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'python -m paper_hunter.cli run-daily "$profile" || true' not in text


def test_daily_workflow_handles_missing_output_directory():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "if [ -d output ]; then" in text
    assert "git add -f output/" in text


def test_daily_workflow_runs_tests():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "python -m pytest -q" in text


def test_daily_workflow_exposes_notification_secrets():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}" in text
    assert "TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}" in text
    assert "SMTP_PASSWORD: ${{ secrets.SMTP_PASSWORD }}" in text
