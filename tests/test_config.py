"""配置加载与校验测试"""
import json
import pytest
from pathlib import Path
from paper_hunter.config import ProfileConfig, load_profile


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
            "type": "feishu",
            "webhook_env": "MEDICAL_WEBHOOK",
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
    assert config.notification.type == "feishu"
    assert config.notification.webhook_env == "MEDICAL_WEBHOOK"


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
