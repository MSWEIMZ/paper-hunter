"""引用数据回填模块（CrossRef API）"""
from __future__ import annotations
import json
import re
import time
import urllib.parse
from urllib.request import urlopen, Request
from urllib.error import HTTPError

_CROSSREF_API = "https://api.crossref.org/works"
_RATE_LIMIT_DELAY = 0.5
_USER_AGENT = "paper-hunter/1.0 (https://github.com/MSWEIMZ/paper-hunter)"


def _query_crossref(title: str) -> dict | None:
    """查询 CrossRef 获取引用数据

    Args:
        title: 论文标题

    Returns:
        {"citation_count": int, "venue": str} 或 None
    """
    clean = re.sub(r'[\$\\{}^_~]', '', title).strip()
    clean = re.sub(r'\s+', ' ', clean)[:100]
    encoded = urllib.parse.quote(clean)
    url = f"{_CROSSREF_API}?query.title={encoded}&rows=1&select=DOI,title,is-referenced-by-count,container-title"

    try:
        req = Request(url, headers={"User-Agent": _USER_AGENT})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("message", {}).get("items", [])
            if items:
                item = items[0]
                cit = item.get("is-referenced-by-count", 0)
                containers = item.get("container-title", [])
                venue = containers[0] if containers else ""
                return {"citation_count": cit, "venue": venue}
    except HTTPError as e:
        if e.code == 429:
            time.sleep(8)
    except Exception:
        pass
    return None


def fill_citations(
    records: list[dict],
    max_fill: int = 100,
    dry_run: bool = False,
) -> tuple[int, list[dict]]:
    """为 citation_count==0 的论文回填引用数据

    Args:
        records: 论文列表
        max_fill: 最大回填数量
        dry_run: 试运行模式

    Returns:
        (成功数, 更新后的记录列表)
    """
    targets = [r for r in records if r.get("citation_count", 0) == 0]
    targets = targets[:max_fill]

    if not targets:
        print("  无需回填的论文")
        return 0, records

    print(f"  待回填: {len(targets)} 篇")

    if dry_run:
        print("  [DRY RUN] 不实际执行")
        return 0, records

    enriched = 0
    for i, rec in enumerate(targets):
        title = rec.get("title", "")
        if not title:
            continue

        result = _query_crossref(title)
        if result:
            rec["citation_count"] = result["citation_count"]
            if result["venue"] and not rec.get("venue"):
                rec["venue"] = result["venue"]
            enriched += 1

        time.sleep(_RATE_LIMIT_DELAY)

        if (i + 1) % 25 == 0:
            print(f"    {i + 1}/{len(targets)} enriched={enriched}")

    print(f"  回填完成: {enriched}/{len(targets)}")
    return enriched, records
