"""OpenAlex 论文搜索源（免费、无限速）"""
from __future__ import annotations
import json
import time
from urllib.request import urlopen, Request
from urllib.parse import urlencode

_BASE_URL = "https://api.openalex.org/works"
_RATE_LIMIT_DELAY = 0.1  # 100ms 间隔


def _normalize_paper(raw: dict) -> dict:
    """将 OpenAlex 返回结果统一为标准 dict 结构"""
    # 提取标题
    title = raw.get("title", "").strip()
    if not title:
        return {}

    # 提取作者
    authorships = raw.get("authorships", [])
    authors = [a.get("author", {}).get("display_name", "Unknown") for a in authorships[:5]]

    # 提取摘要（OpenAlex 用 inverted_abstract）
    abstract = ""
    inv_abs = raw.get("abstract_inverted_index")
    if inv_abs:
        # 反转索引重建摘要
        word_positions = []
        for word, positions in inv_abs.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join(w for _, w in word_positions)

    # 提取年份
    year = raw.get("publication_year", 0)

    # 提取 DOI 和 URL
    doi = raw.get("doi", "")
    url = raw.get("id", "")
    if doi:
        url = doi

    # 提取引用量
    citation_count = raw.get("cited_by_count", 0)

    # 提取 venue/journal
    primary_location = raw.get("primary_location", {}) or {}
    source = primary_location.get("source", {}) or {}
    venue = source.get("display_name", "")

    # 提取 categories
    concepts = raw.get("concepts", [])
    categories = []
    for c in concepts[:3]:
        if c.get("score", 0) > 0.3:
            categories.append(c.get("display_name", ""))

    return {
        "title": title,
        "authors": authors,
        "summary": abstract,
        "url": url,
        "arxiv_url": "",
        "arxiv_id": "",
        "published": f"{year}-01-01" if year else "",
        "updated": "",
        "pdf_url": "",
        "categories": categories,
        "primary_category": "",
        "journal_ref": venue,
        "citation_count": citation_count,
        "venue": venue,
        "source": "openalex",
    }


def search_openalex(query: str, max_results: int = 20) -> list[dict]:
    """搜索 OpenAlex

    Args:
        query: 搜索关键词
        max_results: 最大结果数

    Returns:
        论文列表
    """
    params = {
        "search": query,
        "per_page": min(max_results, 200),
        "sort": "relevance_score:desc",
        "mailto": "paper-hunter@example.com",  # 礼貌池
    }
    url = f"{_BASE_URL}?{urlencode(params)}"

    try:
        req = Request(url, headers={"User-Agent": "paper-hunter/1.0"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] OpenAlex 请求失败: {e}")
        return []

    results = data.get("results", [])
    papers = []
    for raw in results:
        paper = _normalize_paper(raw)
        if paper and paper.get("title"):
            papers.append(paper)
        if len(papers) >= max_results:
            break

    time.sleep(_RATE_LIMIT_DELAY)
    return papers
