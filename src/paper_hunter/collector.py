"""通用论文收集模块（支持 arXiv + Semantic Scholar）"""
from __future__ import annotations
import re
import ssl
import time
from difflib import SequenceMatcher
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from .config import ProfileConfig

try:
    import arxiv
    USE_ARXIV_LIB = True
except ImportError:
    USE_ARXIV_LIB = False


def _search_arxiv_lib(query: str, max_results: int) -> list[dict]:
    """使用 arxiv 库搜索"""
    papers = []
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending,
    )
    for result in client.results(search):
        papers.append({
            "title": result.title.strip(),
            "authors": [a.name for a in result.authors],
            "summary": result.summary.strip(),
            "arxiv_url": result.entry_id,
            "arxiv_id": result.get_short_id(),
            "published": str(result.published.date()),
            "updated": str(result.updated.date()) if result.updated else "",
            "pdf_url": result.pdf_url,
            "categories": [c for c in result.categories if c.startswith("cs.")],
            "primary_category": result.primary_category,
            "journal_ref": getattr(result, "journal_ref", None) or "",
            "citation_count": 0,
            "venue": "",
            "source": "arxiv",
        })
    return papers


def _search_arxiv_manual(query: str, max_results: int) -> list[dict]:
    """手动调用 arXiv API"""
    base_url = "http://export.arxiv.org/api/query?"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    url = base_url + urlencode(params)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urlopen(url, timeout=30, context=ctx) as resp:
            data = resp.read().decode("utf-8")
            return _parse_arxiv_xml(data)
    except Exception as e:
        print(f"  [WARN] arXiv API 请求失败: {e}")
        return []


def _parse_arxiv_xml(xml_data: str) -> list[dict]:
    """解析 arXiv XML 响应"""
    papers = []
    entries = re.findall(r"<entry>(.*?)</entry>", xml_data, re.DOTALL)
    for entry in entries:
        paper: dict = {}
        title_m = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        if title_m:
            paper["title"] = " ".join(title_m.group(1).split())
        authors = re.findall(r"<name>(.*?)</name>", entry)
        paper["authors"] = authors or ["Unknown"]
        summary_m = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
        if summary_m:
            paper["summary"] = " ".join(summary_m.group(1).split())
        id_m = re.search(r"<id>(.*?)</id>", entry)
        if id_m:
            paper["arxiv_url"] = id_m.group(1)
            paper["arxiv_id"] = id_m.group(1).split("/")[-1]
        pub_m = re.search(r"<published>(.*?)</published>", entry)
        if pub_m:
            paper["published"] = pub_m.group(1)[:10]
        upd_m = re.search(r"<updated>(.*?)</updated>", entry)
        if upd_m:
            paper["updated"] = upd_m.group(1)[:10]
        pdf_m = re.search(r'<link[^>]*title="pdf"[^>]*href="(.*?)"', entry)
        if pdf_m:
            paper["pdf_url"] = pdf_m.group(1)
        cats = re.findall(r'<category term="([^"]*)"', entry)
        paper["categories"] = [c for c in cats if c.startswith("cs.")]
        paper["primary_category"] = paper["categories"][0] if paper["categories"] else ""
        jr_m = re.search(r"<journal-ref>(.*?)</journal-ref>", entry, re.DOTALL)
        paper["journal_ref"] = jr_m.group(1).strip() if jr_m else ""
        paper["citation_count"] = 0
        paper["venue"] = ""
        paper["source"] = "arxiv"
        if paper.get("title"):
            papers.append(paper)
    return papers


def _search_one_query(query: str, max_results: int) -> list[dict]:
    """执行单条 arXiv 查询"""
    if USE_ARXIV_LIB:
        return _search_arxiv_lib(query, max_results)
    return _search_arxiv_manual(query, max_results)


def _pre_filter(paper: dict, blocked_keywords: list[str]) -> bool:
    """返回 True 表示应被阻断（命中黑名单）"""
    text = (paper.get("title", "") + " " + paper.get("summary", "")).lower()
    return any(kw.lower() in text for kw in blocked_keywords)


def _is_duplicate(paper_a: dict, paper_b: dict) -> bool:
    """判断两篇论文是否重复"""
    id_a = paper_a.get("arxiv_id", "")
    id_b = paper_b.get("arxiv_id", "")
    if id_a and id_b and id_a == id_b:
        return True
    title_a = paper_a.get("title", "").lower()
    title_b = paper_b.get("title", "").lower()
    if title_a and title_b:
        ratio = SequenceMatcher(None, title_a, title_b).ratio()
        if ratio > 0.85:
            return True
    return False


def _dedup(new_papers: list[dict], seen_ids: set[str]) -> list[dict]:
    """去重：与已有 ID 和内部重复"""
    unique = []
    for paper in new_papers:
        aid = paper.get("arxiv_id", "")
        if aid and aid in seen_ids:
            continue
        is_dup = False
        for existing in unique:
            if _is_duplicate(paper, existing):
                is_dup = True
                break
        if not is_dup:
            unique.append(paper)
            if aid:
                seen_ids.add(aid)
    return unique


def collect_candidates(config: ProfileConfig) -> list[tuple[str, str, dict]]:
    """收集所有候选论文

    Returns:
        [(query_type, search_query, raw_paper), ...]
    """
    max_results = config.runtime.max_results_per_query
    blocked = config.filters.blocked_keywords
    seen_ids: set[str] = set()
    candidates: list[tuple[str, str, dict]] = []

    query_groups = [
        ("core", config.core_queries),
        ("expanded", config.expanded_queries),
        ("exploratory", config.exploratory_queries),
    ]

    for query_type, queries in query_groups:
        for query in queries:
            print(f"  [{query_type}] {query[:50]}...")
            raw_papers = _search_one_query(query, max_results)
            new_papers = _dedup(raw_papers, seen_ids)
            kept = 0
            for paper in new_papers:
                if _pre_filter(paper, blocked):
                    continue
                candidates.append((query_type, query, paper))
                kept += 1
            print(f"    新论文: {len(new_papers)}, 通过预过滤: {kept}")
            time.sleep(3)  # arXiv rate limit

    print(f"\n候选池总计: {len(candidates)} 篇")
    return candidates
