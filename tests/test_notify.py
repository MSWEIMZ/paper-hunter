"""通知模块测试"""
import pytest
import os
from paper_hunter.notify import _get_webhook, _build_feishu_card


def test_get_webhook_from_env(monkeypatch):
    """应该从环境变量读取 webhook"""
    monkeypatch.setenv("TEST_WEBHOOK", "https://example.com/hook")
    assert _get_webhook("TEST_WEBHOOK") == "https://example.com/hook"


def test_get_webhook_empty(monkeypatch):
    """未设置环境变量应该返回空字符串"""
    monkeypatch.delenv("NONEXISTENT_WEBHOOK", raising=False)
    assert _get_webhook("NONEXISTENT_WEBHOOK") == ""


def test_build_feishu_card_basic():
    """应该能构建飞书卡片消息"""
    new_papers = [
        {
            "title": "Test Paper A",
            "authors": ["Alice", "Bob"],
            "url": "https://arxiv.org/abs/2401.00001",
            "relevance_score": 5.0,
            "quality_label": "core",
            "citation_count": 10,
            "venue": "CVPR",
            "summary_zh": "测试摘要",
        },
    ]
    stats = {"total": 100, "by_label": {"core": 30, "strongly_related": 60, "noise": 10}}
    card = _build_feishu_card("Test Profile", new_papers, stats)
    assert "Test Profile" in str(card)
    assert "Test Paper A" in str(card)


def test_build_feishu_card_empty():
    """无新增论文时应该构建简报"""
    stats = {"total": 100, "by_label": {"core": 30}}
    card = _build_feishu_card("Test Profile", [], stats)
    assert "Test Profile" in str(card)
