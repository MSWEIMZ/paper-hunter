"""多维度评分测试"""
import pytest
from paper_hunter.scorer import (
    compute_novelty_score,
    compute_impact_score,
    compute_hotness_score,
    compute_multi_dimension_score,
)


def _make_paper(year=2024, citation_count=0, citations_recent=None):
    return {
        "year": year,
        "citation_count": citation_count,
        "citations_recent": citations_recent or [],
    }


# ── Novelty（新颖性）─────────────────────────────────────────
def test_novelty_current_year():
    """当前年份应该得最高分"""
    assert compute_novelty_score(2026, current_year=2026) == 1.0


def test_novelty_one_year_ago():
    """去年应该得 0.8"""
    assert compute_novelty_score(2025, current_year=2026) == 0.8


def test_novelty_old():
    """5 年前应该低于 0.5"""
    score = compute_novelty_score(2021, current_year=2026)
    assert score < 0.5


def test_novelty_very_old():
    """10 年前应该很低"""
    score = compute_novelty_score(2016, current_year=2026)
    assert score < 0.3


# ── Impact（影响力）─────────────────────────────────────────
def test_impact_no_citations():
    """无引用应该为 0"""
    assert compute_impact_score(0) == 0.0


def test_impact_low():
    """少量引用应该低分"""
    score = compute_impact_score(10)
    assert 0 < score < 0.5


def test_impact_medium():
    """中等引用"""
    score = compute_impact_score(100)
    assert 0.4 < score < 1.0


def test_impact_high():
    """高引用应该接近 1.0"""
    score = compute_impact_score(1000)
    assert score >= 0.7


def test_impact_saturation():
    """超高引用不应超过 1.0"""
    score = compute_impact_score(10000)
    assert score <= 1.0


# ── Hotness（热度）─────────────────────────────────────────
def test_hotness_no_recent():
    """无近期引用数据，用总引用估算"""
    score = compute_hotness_score(citation_count=50, citations_recent=[])
    assert score >= 0


def test_hotness_with_recent():
    """有近期引用应该更高"""
    score_no = compute_hotness_score(citation_count=50, citations_recent=[])
    score_yes = compute_hotness_score(citation_count=50, citations_recent=[10, 20, 30])
    assert score_yes >= score_no


def test_hotness_high_recent():
    """近期引用爆发应该高热度"""
    score = compute_hotness_score(citation_count=100, citations_recent=[50, 60, 70])
    assert score > 0.5


# ── Multi-dimension 综合评分 ─────────────────────────────
def test_multi_dimension_returns_dict():
    """应该返回多维度分数 dict"""
    paper = _make_paper(year=2025, citation_count=100)
    result = compute_multi_dimension_score(paper, relevance=4.0)
    assert "relevance" in result
    assert "novelty" in result
    assert "impact" in result
    assert "hotness" in result
    assert "composite" in result


def test_multi_dimension_composite_weighted():
    """综合分应该是加权平均"""
    paper = _make_paper(year=2026, citation_count=500)
    result = compute_multi_dimension_score(paper, relevance=5.0)
    assert result["composite"] > 0
    assert result["composite"] <= 10.0


def test_multi_dimension_old_low_cite():
    """老论文低引用应该综合分低"""
    paper = _make_paper(year=2016, citation_count=5)
    result = compute_multi_dimension_score(paper, relevance=3.0)
    assert result["composite"] < 3.0
