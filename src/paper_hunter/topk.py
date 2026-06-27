"""每日 Top K 推荐模块"""
from __future__ import annotations
from .scorer import compute_multi_dimension_score


def select_top_k(
    new_papers: list[dict],
    k: int = 5,
    current_year: int | None = None,
) -> list[dict]:
    """从新增论文中选出最值得读的 K 篇

    使用多维度综合评分排序。

    Args:
        new_papers: 新增论文列表（已包含 relevance_score）
        k: 推荐数量
        current_year: 当前年份

    Returns:
        Top K 论文列表（按 composite 降序）
    """
    if not new_papers:
        return []

    scored = []
    for p in new_papers:
        relevance = p.get("relevance_score", 0)
        multi = compute_multi_dimension_score(p, relevance, current_year)
        p["multi_score"] = multi
        scored.append(p)

    scored.sort(key=lambda r: -r["multi_score"]["composite"])
    return scored[:k]


def format_top_k_markdown(top_papers: list[dict], lang: str = "zh") -> str:
    """格式化 Top K 为 Markdown"""
    if not top_papers:
        return ""

    lines = []
    if lang == "zh":
        lines.append("## 🏆 今日推荐 Top K")
    else:
        lines.append("## 🏆 Today's Top Picks")
    lines.append("")

    for i, p in enumerate(top_papers, 1):
        title = p.get("title", "")
        url = p.get("url", "#")
        authors = ", ".join(p.get("authors", [])[:2])
        if len(p.get("authors", [])) > 2:
            authors += "+"
        summary = p.get("summary_zh", p.get("one_line_summary", ""))[:80]
        multi = p.get("multi_score", {})
        composite = multi.get("composite", 0)
        novelty = multi.get("novelty", 0)
        impact = multi.get("impact", 0)
        hotness = multi.get("hotness", 0)

        lines.append(f"### {i}. [{title}]({url})")
        if lang == "zh":
            lines.append(f"**作者**: {authors} | **综合分**: {composite} | **新颖性**: {novelty} | **影响力**: {impact} | **热度**: {hotness}")
        else:
            lines.append(f"**Authors**: {authors} | **Composite**: {composite} | **Novelty**: {novelty} | **Impact**: {impact} | **Hotness**: {hotness}")
        if summary:
            lines.append(f"> {summary}")
        lines.append("")

    return "\\n".join(lines)
