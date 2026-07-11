from paper_hunter.topk import format_top_k_markdown


def test_format_top_k_uses_real_newlines():
    markdown = format_top_k_markdown([{
        "title": "A Paper",
        "url": "https://example.com",
        "authors": ["Ada"],
        "multi_score": {
            "composite": 8.0,
            "novelty": 1.0,
            "impact": 0.5,
            "hotness": 0.4,
        },
    }])

    assert "\n### 1." in markdown
    assert "\\n" not in markdown
