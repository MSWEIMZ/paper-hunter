"""论文收集器测试"""
import pytest
from paper_hunter.collector import _pre_filter, _is_duplicate, _search_builtin_source


def test_pre_filter_blocks():
    """命中屏蔽关键词应该返回 True"""
    paper = {"title": "Cooking Recipe Generation", "abstract": "A recipe system."}
    assert _pre_filter(paper, ["cooking"]) is True


def test_pre_filter_passes():
    """未命中屏蔽关键词应该返回 False"""
    paper = {"title": "Medical Image Segmentation", "abstract": "Deep learning for imaging."}
    assert _pre_filter(paper, ["cooking"]) is False


def test_pre_filter_empty_blocked():
    """空屏蔽列表应该放行"""
    paper = {"title": "Any Paper", "abstract": "Any abstract."}
    assert _pre_filter(paper, []) is False


def test_is_duplicate_same_arxiv_id():
    """相同 arxiv_id 应该判重"""
    a = {"arxiv_id": "2401.12345"}
    b = {"arxiv_id": "2401.12345"}
    assert _is_duplicate(a, b) is True


def test_is_duplicate_different_arxiv_id():
    """不同 arxiv_id 不应判重"""
    a = {"arxiv_id": "2401.12345"}
    b = {"arxiv_id": "2401.67890"}
    assert _is_duplicate(a, b) is False


def test_is_duplicate_similar_title():
    """标题高度相似应该判重"""
    a = {"arxiv_id": "", "title": "Deep Learning for Medical Image Segmentation"}
    b = {"arxiv_id": "", "title": "Deep Learning for Medical Image Segmentation and Analysis"}
    assert _is_duplicate(a, b) is True


def test_unsupported_builtin_source_fails_clearly():
    with pytest.raises(ValueError, match="不支持的数据源"):
        _search_builtin_source("query", "crossref", 5)
