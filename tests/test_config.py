"""配置加载与校验测试"""
import json
import pytest
from pathlib import Path
from paper_hunter.config import ProfileConfig, load_profile
from paper_hunter.cli import _build_sources_config


def test_load_minimal_profile(tmp_path):
    """最小配置应该能正确加载"""
    profile = {
        "profile_name": "Test Domain",
        "queries": {
            "core": ["deep learning test"],
        },
    }
    p = tmp_path / "test.json"
    p.write_text(json.dumps(profile), encoding="utf-8")

    config = load_profile(p)
    assert config.profile_name == "Test Domain"
    assert config.core_queries == ["deep learning test"]
    assert config.filters.years_from == 2015  # default
    assert config.scoring.min_relevance_score == 2.5  # default


def test_load_full_profile(tmp_path):
    """完整配置应该能正确加载所有字段"""
    profile = {
        "profile_name": "Medical AI",
        "description": "医学影像 AI 论文",
        "output_dir": "medical_papers",
        "queries": {
            "core": ["medical image segmentation"],
            "expanded": ["radiology AI"],
            "exploratory": ["clinical decision support"],
        },
        "domain_keywords": ["medical", "clinical", "radiology"],
        "filters": {
            "years_from": 2020,
            "years_to": 2026,
            "allowed_categories": ["cs.CV", "q-bio"],
            "blocked_keywords": ["irrelevant"],
        },
        "scoring": {
            "min_relevance_score": 3.0,
            "core_threshold": 4.5,
        },
        "notification": {
            "type": "telegram",
            "webhook_env": "MEDICAL_WEBHOOK",
            "telegram_token_env": "TG_TOKEN",
            "telegram_chat_env": "TG_CHAT",
            "smtp_host": "smtp.example.com",
            "smtp_port": 465,
            "smtp_user": "sender@example.com",
            "smtp_password_env": "SMTP_PASSWORD",
            "to_email": "reader@example.com",
        },
    }
    p = tmp_path / "medical.json"
    p.write_text(json.dumps(profile), encoding="utf-8")

    config = load_profile(p)
    assert config.profile_name == "Medical AI"
    assert config.description == "医学影像 AI 论文"
    assert config.output_dir == "medical_papers"
    assert config.domain_keywords == ["medical", "clinical", "radiology"]
    assert config.filters.years_from == 2020
    assert config.filters.years_to == 2026
    assert "q-bio" in config.filters.allowed_categories
    assert config.scoring.min_relevance_score == 3.0
    assert config.notification.type == "telegram"
    assert config.notification.webhook_env == "MEDICAL_WEBHOOK"
    assert config.notification.telegram_token_env == "TG_TOKEN"
    assert config.notification.telegram_chat_env == "TG_CHAT"
    assert config.notification.smtp_host == "smtp.example.com"
    assert config.notification.smtp_port == 465
    assert config.notification.smtp_user == "sender@example.com"
    assert config.notification.smtp_password_env == "SMTP_PASSWORD"
    assert config.notification.to_email == "reader@example.com"


def test_missing_queries_raises(tmp_path):
    """缺少 queries.core 应该报错"""
    profile = {"profile_name": "Bad Config"}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(profile), encoding="utf-8")

    with pytest.raises(ValueError, match="queries.core"):
        load_profile(p)


def test_missing_file_raises():
    """文件不存在应该报错"""
    with pytest.raises(FileNotFoundError):
        load_profile("/nonexistent/profile.json")


def test_build_sources_config_is_json_serializable():
    raw = _build_sources_config(["arxiv", "semantic_scholar"])

    assert raw["builtin"]["arxiv"]["enabled"] is True
    assert raw["builtin"]["semantic_scholar"]["enabled"] is True
    assert raw["builtin"]["openalex"]["enabled"] is False
    json.dumps(raw)
