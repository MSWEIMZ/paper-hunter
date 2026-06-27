"""评分器测试"""
import pytest
from paper_hunter.scorer import compute_score, assign_label
from paper_hunter.config import ScoringConfig


def _make_paper(title="", abstract="", citation_count=0, venue="", categories=None):
    return {
        "title": title,
        "abstract": abstract,
        "citation_count": citation_count,
        "venue": venue,
        "categories": categories or [],
    }


def test_core_query_high_score():
    """core 查询的论文应该得到高分"""
    paper = _make_paper(
        title="Deep Learning for Medical Image Segmentation",
        abstract="We propose a novel deep learning approach for medical image segmentation.",
    )
    score = compute_score(paper, "core", "medical image segmentation deep learning")
    assert score >= 2.0


def test_blocked_keyword_negative():
    """命中屏蔽关键词应该大幅扣分"""
    config = ScoringConfig(blocked_penalty=10.0)
    paper = _make_paper(
        title="Irrelevant Paper about Cooking",
        abstract="This paper is about cooking recipes.",
    )
    score = compute_score(paper, "core", "medical image", blocked_keywords=["cooking"], config=config)
    assert score < 0


def test_venue_bonus():
    """顶级会议应该加分"""
    paper = _make_paper(
        title="Medical Image Analysis",
        abstract="A medical image analysis paper published at CVPR.",
        venue="CVPR 2024",
    )
    score_with_venue = compute_score(paper, "core", "medical image analysis")
    paper_no_venue = _make_paper(
        title="Medical Image Analysis",
        abstract="A medical image analysis paper.",
    )
    score_no_venue = compute_score(paper_no_venue, "core", "medical image analysis")
    assert score_with_venue > score_no_venue


def test_citation_bonus():
    """高引用应该加分"""
    paper_high = _make_paper(
        title="Medical Image Segmentation Survey",
        abstract="A comprehensive survey of medical image segmentation.",
        citation_count=100,
    )
    paper_low = _make_paper(
        title="Medical Image Segmentation Survey",
        abstract="A comprehensive survey of medical image segmentation.",
        citation_count=5,
    )
    score_high = compute_score(paper_high, "core", "medical image segmentation survey")
    score_low = compute_score(paper_low, "core", "medical image segmentation survey")
    assert score_high > score_low


def test_assign_label_core():
    """高分应该标记为 core"""
    assert assign_label(5.0, min_score=2.5, core_threshold=4.0) == "core"


def test_assign_label_strongly_related():
    """中分应该标记为 strongly_related"""
    assert assign_label(3.0, min_score=2.5, core_threshold=4.0) == "strongly_related"


def test_assign_label_noise():
    """低分应该标记为 noise"""
    assert assign_label(1.0, min_score=2.5, core_threshold=4.0) == "noise"


def test_domain_keywords_bonus():
    """域关键词命中应该加分"""
    paper = _make_paper(
        title="Medical Image Segmentation with Deep Learning",
        abstract="We present a deep learning method for medical image segmentation.",
    )
    score_with_domain = compute_score(
        paper, "core", "image segmentation",
        domain_keywords=["medical", "clinical"],
    )
    score_without = compute_score(
        paper, "core", "image segmentation",
        domain_keywords=[],
    )
    assert score_with_domain > score_without
