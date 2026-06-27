"""论文数据规范化模块"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class PaperRecord:
    """标准化论文记录"""
    canonical_id: str = ""
    version: int = 1
    arxiv_id: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int = 0
    published: str = ""
    updated: str = ""
    primary_category: str = ""
    categories: list[str] = field(default_factory=list)
    abstract: str = ""
    url: str = ""
    pdf_url: str = ""
    journal_ref: str = ""
    query_type: str = ""
    search_query: str = ""
    relevance_score: float = 0.0
    quality_label: str = ""
    markdown_path: str = ""
    citation_count: int = 0
    venue: str = ""
    source: str = "arxiv"

    # 扩展字段（通用）
    one_line_summary: str = ""
    summary_zh: str = ""
    method_type: str = ""
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "canonical_id": self.canonical_id,
            "version": self.version,
            "arxiv_id": self.arxiv_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "published": self.published,
            "updated": self.updated,
            "primary_category": self.primary_category,
            "categories": self.categories,
            "abstract": self.abstract,
            "url": self.url,
            "pdf_url": self.pdf_url,
            "journal_ref": self.journal_ref,
            "query_type": self.query_type,
            "search_query": self.search_query,
            "relevance_score": self.relevance_score,
            "quality_label": self.quality_label,
            "markdown_path": self.markdown_path,
            "citation_count": self.citation_count,
            "venue": self.venue,
            "source": self.source,
            "one_line_summary": self.one_line_summary,
            "summary_zh": self.summary_zh,
            "method_type": self.method_type,
            "topics": self.topics,
        }


def normalize_arxiv_id(raw_id: str) -> tuple[str, int]:
    """规范化 arXiv ID -> (canonical_id, version)"""
    if not raw_id:
        return ("unknown", 1)
    raw_id = raw_id.split("/")[-1]
    match = re.match(r"^(\d{4}\.\d{4,5})(?:v(\d+))?$", raw_id)
    if match:
        canonical = match.group(1)
        version = int(match.group(2)) if match.group(2) else 1
        return (canonical, version)
    return (raw_id, 1)


def extract_year_from_arxiv_id(arxiv_id: str) -> int:
    """从 arXiv ID 提取年份"""
    match = re.match(r"(\d{2})(\d{2})", arxiv_id)
    if match:
        year_prefix = int(match.group(1))
        year = 2000 + year_prefix if year_prefix < 90 else 1900 + year_prefix
        return year
    return 2020


def extract_year(published: str, arxiv_id: str) -> int:
    """从 published 日期或 arxiv_id 提取年份"""
    if published and len(published) >= 4:
        try:
            return int(published[:4])
        except ValueError:
            pass
    return extract_year_from_arxiv_id(arxiv_id)


def build_paper_record(raw: dict, query_type: str, search_query: str) -> PaperRecord:
    """从原始数据构建标准化论文记录"""
    source = raw.get("source", "arxiv")

    raw_arxiv_id = raw.get("arxiv_id", raw.get("arxiv_url", "").split("/")[-1])
    ss_paper_id = raw.get("paperId", "")

    if raw_arxiv_id:
        canonical_id, version = normalize_arxiv_id(raw_arxiv_id)
    elif ss_paper_id:
        canonical_id = ss_paper_id
        version = 1
    else:
        canonical_id = "unknown"
        version = 1

    published = raw.get("published", raw.get("publicationDate", ""))
    year = extract_year(published, canonical_id if raw_arxiv_id else "")
    categories = raw.get("categories", [])
    primary = categories[0] if categories else ""

    if source == "semantic_scholar":
        citation_count = raw.get("citation_count", raw.get("citationCount", 0))
        venue_raw = raw.get("venue", "")
        if isinstance(venue_raw, dict):
            venue = venue_raw.get("name", "")
        else:
            venue = venue_raw
        abstract = raw.get("summary", raw.get("abstract", "")).strip()
        url = raw.get("url", raw.get("arxiv_url", ""))
        if not url and ss_paper_id:
            url = f"https://www.semanticscholar.org/paper/{ss_paper_id}"
    else:
        citation_count = raw.get("citation_count", 0)
        venue = raw.get("venue", "")
        abstract = raw.get("summary", "").strip()
        url = raw.get("arxiv_url", "")

    return PaperRecord(
        canonical_id=canonical_id,
        version=version,
        arxiv_id=raw_arxiv_id or "",
        title=raw.get("title", "").strip(),
        authors=raw.get("authors", []),
        year=year,
        published=published,
        updated=raw.get("updated", ""),
        primary_category=primary,
        categories=categories,
        abstract=abstract,
        url=url,
        pdf_url=raw.get("pdf_url", ""),
        journal_ref=raw.get("journal_ref", raw.get("venue", "")),
        query_type=query_type,
        search_query=search_query,
        citation_count=citation_count,
        venue=venue,
        source=source,
    )
