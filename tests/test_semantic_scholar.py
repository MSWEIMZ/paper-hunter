from paper_hunter.sources.semantic_scholar import _normalize_paper


def test_normalize_semantic_scholar_paper():
    paper = _normalize_paper({
        "paperId": "abc123",
        "externalIds": {"ArXiv": "2601.12345"},
        "title": "A Paper",
        "abstract": "Abstract",
        "authors": [{"name": "Ada"}],
        "year": 2026,
        "publicationDate": "2026-01-02",
        "url": "https://example.com/paper",
        "openAccessPdf": {"url": "https://example.com/paper.pdf"},
        "citationCount": 42,
        "venue": "CVPR",
        "fieldsOfStudy": ["Computer Science"],
    })

    assert paper["paperId"] == "abc123"
    assert paper["arxiv_id"] == "2601.12345"
    assert paper["authors"] == ["Ada"]
    assert paper["citation_count"] == 42
    assert paper["source"] == "semantic_scholar"
