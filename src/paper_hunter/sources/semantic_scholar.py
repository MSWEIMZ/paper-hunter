"""Semantic Scholar Academic Graph 数据源。"""
from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = (
    "title,abstract,authors,year,publicationDate,url,openAccessPdf,"
    "citationCount,venue,fieldsOfStudy,externalIds"
)


def _normalize_paper(raw: dict) -> dict:
    """把 Academic Graph 响应转换为内部统一字段。"""
    external_ids = raw.get("externalIds") or {}
    open_access_pdf = raw.get("openAccessPdf") or {}
    authors = raw.get("authors") or []
    return {
        "paperId": raw.get("paperId", ""),
        "arxiv_id": external_ids.get("ArXiv", ""),
        "title": raw.get("title") or "",
        "authors": [author.get("name", "") for author in authors if author.get("name")],
        "summary": raw.get("abstract") or "",
        "published": raw.get("publicationDate") or str(raw.get("year") or ""),
        "updated": "",
        "url": raw.get("url") or "",
        "pdf_url": open_access_pdf.get("url", ""),
        "categories": [],
        "primary_category": "",
        "citation_count": raw.get("citationCount") or 0,
        "venue": raw.get("venue") or "",
        "source": "semantic_scholar",
    }


def search_semantic_scholar(query: str, max_results: int = 20) -> list[dict]:
    """按相关性搜索论文；无需 API Key，受公共接口限流约束。"""
    params = urlencode({
        "query": query.replace("-", " "),
        "limit": max(1, min(max_results, 100)),
        "fields": FIELDS,
    })
    request = Request(
        f"{API_URL}?{params}",
        headers={"User-Agent": "paper-hunter/1.0"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        print(f"  [WARN] Semantic Scholar API 请求失败: {exc}")
        return []
    return [_normalize_paper(paper) for paper in payload.get("data", [])]
