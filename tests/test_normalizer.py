"""论文规范化测试"""
import pytest
from paper_hunter.normalizer import normalize_arxiv_id, extract_year, build_paper_record


def test_normalize_arxiv_id_with_version():
    assert normalize_arxiv_id("2603.04976v2") == ("2603.04976", 2)


def test_normalize_arxiv_id_without_version():
    assert normalize_arxiv_id("2603.04976") == ("2603.04976", 1)


def test_normalize_arxiv_id_with_url():
    assert normalize_arxiv_id("http://arxiv.org/abs/2603.04976v1") == ("2603.04976", 1)


def test_normalize_arxiv_id_empty():
    assert normalize_arxiv_id("") == ("unknown", 1)


def test_extract_year_from_published():
    assert extract_year("2024-03-18", "2603.04976") == 2024


def test_extract_year_from_arxiv_id():
    assert extract_year("", "2603.04976") == 2026


def test_build_paper_record():
    raw = {
        "title": "Test Paper",
        "authors": ["Alice", "Bob"],
        "summary": "A test abstract.",
        "arxiv_url": "http://arxiv.org/abs/2401.12345v1",
        "arxiv_id": "2401.12345v1",
        "published": "2024-01-20",
        "categories": ["cs.CV"],
        "citation_count": 10,
        "venue": "CVPR",
        "source": "arxiv",
    }
    rec = build_paper_record(raw, "core", "test query")
    assert rec.canonical_id == "2401.12345"
    assert rec.version == 1
    assert rec.title == "Test Paper"
    assert rec.year == 2024
    assert rec.citation_count == 10
    assert rec.query_type == "core"


def test_build_paper_record_semantic_scholar():
    raw = {
        "title": "SS Paper",
        "authors": ["Charlie"],
        "summary": "An SS abstract.",
        "paperId": "abc123",
        "published": "2023-06-01",
        "citation_count": 50,
        "venue": "NeurIPS",
        "source": "semantic_scholar",
    }
    rec = build_paper_record(raw, "expanded", "test ss query")
    assert rec.canonical_id == "abc123"
    assert rec.year == 2023
    assert rec.source == "semantic_scholar"
