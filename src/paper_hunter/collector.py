"""通用论文收集模块（支持 arXiv + Semantic Scholar）"""
from __future__ import annotations
import re
import ssl
import time
from difflib import SequenceMatcher
from urllib.request import urlopen, Request
from urllib.parse import urlencode

from .config import ProfileConfig
from .sources_config import SourcesConfig, BuiltinSourceConfig, CustomSourceConfig
from .sources.openalex import search_openalex
from .sources.custom_source import search_custom_source

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


def _search_builtin_source(query: str, source_name: str, max_results: int) -> list[dict]:
    """搜索内置数据源"""
    if source_name == "arxiv":
        return _search_one_query(query, max_results)
    elif source_name == "semantic_scholar":
        from .sources.semantic_scholar import search_semantic_scholar
        return search_semantic_scholar(query, max_results)
    elif source_name == "openalex":
        return search_openalex(query, max_results)
    else:
        return []


def collect_candidates(
    config: ProfileConfig,
    sources_config: SourcesConfig | None = None,
) -> list[tuple[str, str, dict]]:
    """收集所有候选论文

    Args:
        config: Profile 配置
        sources_config: 数据源配置（可选）

    Returns:
        [(query_type, search_query, raw_paper), ...]
    """
    blocked = config.filters.blocked_keywords
    seen_ids: set[str] = set()
    candidates: list[tuple[str, str, dict]] = []

    # 确定启用的数据源
    if sources_config is None:
        sources_config = SourcesConfig()

    enabled_sources = []
    for name, src_cfg in sources_config.builtin.items():
        if src_cfg.enabled:
            enabled_sources.append((name, src_cfg.max_results))
    has_custom = bool(sources_config.custom)

    if not enabled_sources and not has_custom:
        print("  [WARN] 未启用任何数据源，使用默认 arXiv")
        enabled_sources = [("arxiv", 30)]

    print(f"  启用数据源: {[s[0] for s in enabled_sources]}")
    if sources_config.custom:
        print(f"  自定义数据源: {[c.name for c in sources_config.custom]}")

    query_groups = [
        ("core", config.core_queries),
        ("expanded", config.expanded_queries),
        ("exploratory", config.exploratory_queries),
    ]

    for query_type, queries in query_groups:
        for query in queries:
            print(f"\n  [{query_type}] {query[:50]}...")

            # 搜索所有启用的内置数据源
            all_papers = []
            for source_name, max_results in enabled_sources:
                print(f"    搜索 {source_name}...")
                raw_papers = _search_builtin_source(query, source_name, max_results)
                all_papers.extend(raw_papers)
                if source_name == "arxiv":
                    time.sleep(3)  # arXiv rate limit

            # 搜索自定义数据源
            for custom_src in sources_config.custom:
                if custom_src.enabled:
                    print(f"    搜索 {custom_src.name}...")
                    raw_papers = search_custom_source(query, custom_src)
                    all_papers.extend(raw_papers)

            # 去重和过滤
            new_papers = _dedup(all_papers, seen_ids)
            kept = 0
            for paper in new_papers:
                if _pre_filter(paper, blocked):
                    continue
                candidates.append((query_type, query, paper))
                kept += 1
            print(f"    合并去重后: {len(new_papers)}, 通过预过滤: {kept}")

    print(f"\n候选池总计: {len(candidates)} 篇")
    return candidates
