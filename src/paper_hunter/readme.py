"""README 自动生成模块"""
from __future__ import annotations
from datetime import datetime
from collections import defaultdict


def generate_readme(
    records: list[dict],
    stats: dict,
    profile_name: str = "Paper Hunter",
    description: str = "",
    lang: str = "en",
) -> str:
    """生成 README 内容

    Args:
        records: 论文列表
        stats: 统计信息
        profile_name: 配置名称
        description: 描述
        lang: 语言 (en/zh)

    Returns:
        README Markdown 内容
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = stats.get("total", len(records))
    by_label = stats.get("by_label", {})
    core_count = by_label.get("core", 0)
    strong_count = by_label.get("strongly_related", 0)

    lines = []

    # 标题
    if lang == "zh":
        lines.append(f"# 📚 {profile_name}")
        lines.append("")
        if description:
            lines.append(f"> {description}")
            lines.append("")
        lines.append("## 📊 统计概览")
        lines.append("")
        lines.append(f"- **论文总数**: {total}")
        lines.append(f"- **核心论文**: {core_count}")
        lines.append(f"- **高相关论文**: {strong_count}")
        lines.append(f"- **最后更新**: {now}")
    else:
        lines.append(f"# 📚 {profile_name}")
        lines.append("")
        if description:
            lines.append(f"> {description}")
            lines.append("")
        lines.append("## 📊 Overview")
        lines.append("")
        lines.append(f"- **Total Papers**: {total}")
        lines.append(f"- **Core Papers**: {core_count}")
        lines.append(f"- **Strongly Related**: {strong_count}")
        lines.append(f"- **Last Updated**: {now}")
    lines.append("")

    # 高引用 Top 5
    cited = [r for r in records if r.get("citation_count", 0) > 0]
    cited.sort(key=lambda r: -(r["citation_count"] ** 0.5 * r.get("relevance_score", 1)))
    top5 = cited[:5]

    if top5:
        if lang == "zh":
            lines.append("## 🏆 高引用论文 Top 5")
        else:
            lines.append("## 🏆 Top 5 Most Cited")
        lines.append("")
        if lang == "zh":
            lines.append("| 排名 | 标题 | 引用数 | 分数 |")
        else:
            lines.append("| Rank | Title | Citations | Score |")
        lines.append("|------|------|--------|------|")
        for i, p in enumerate(top5, 1):
            title = p.get("title", "")[:60]
            url = p.get("url", "#")
            cit = p.get("citation_count", 0)
            score = p.get("relevance_score", 0)
            lines.append(f"| {i} | [{title}]({url}) | {cit} | {score} |")
        lines.append("")

    # 最新核心论文
    core_papers = [r for r in records if r.get("quality_label") == "core"]
    core_papers.sort(key=lambda r: (-r.get("year", 0), -r.get("relevance_score", 0)))
    latest_core = core_papers[:20]

    if latest_core:
        if lang == "zh":
            lines.append("## 🔥 最新核心论文")
            lines.append("")
            lines.append("| 年份 | 标题 | 摘要 | 作者 | 分数 |")
        else:
            lines.append("## 🔥 Latest Core Papers")
            lines.append("")
            lines.append("| Year | Title | Summary | Author | Score |")
        lines.append("|------|------|------|------|------|")
        for p in latest_core:
            title = p.get("title", "")[:60]
            url = p.get("url", "#")
            summary = p.get("summary_zh", p.get("one_line_summary", ""))[:80]
            authors = ", ".join(p.get("authors", [])[:2])
            if len(p.get("authors", [])) > 2:
                authors += "+"
            year = p.get("year", "")
            score = p.get("relevance_score", 0)
            lines.append(f"| {year} | [{title}]({url}) | {summary} | {authors} | {score} |")
        lines.append("")

    # 年份折叠视图
    by_year: dict[int, list[dict]] = defaultdict(list)
    for r in records:
        if r.get("quality_label") in ("core", "strongly_related"):
            by_year[r.get("year", 0)].append(r)

    if by_year:
        if lang == "zh":
            lines.append("## 📅 按年份浏览")
        else:
            lines.append("## 📅 Browse by Year")
        lines.append("")

        label_icon = {"core": "🔥", "strongly_related": "📎"}
        for year in sorted(by_year.keys(), reverse=True):
            year_papers = sorted(by_year[year], key=lambda r: -r.get("relevance_score", 0))
            count = len(year_papers)
            if lang == "zh":
                lines.append(f"<details>")
                lines.append(f"<summary>📅 {year} 年 ({count} 篇)</summary>")
            else:
                lines.append(f"<details>")
                lines.append(f"<summary>📅 {year} ({count} papers)</summary>")
            lines.append("")
            if lang == "zh":
                lines.append("| 标签 | 标题 | 摘要 | 分数 |")
            else:
                lines.append("| Tag | Title | Summary | Score |")
            lines.append("|------|------|------|------|")
            for p in year_papers:
                icon = label_icon.get(p.get("quality_label", ""), "📝")
                title = p.get("title", "")[:50]
                url = p.get("url", "#")
                summary = p.get("summary_zh", p.get("one_line_summary", ""))[:70]
                score = p.get("relevance_score", 0)
                lines.append(f"| {icon} | [{title}]({url}) | {summary} | {score} |")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    # 底部
    lines.append("---")
    lines.append("")
    if lang == "zh":
        lines.append("🤖 由 [Paper Hunter](https://github.com/MSWEIMZ/paper-hunter) 自动生成")
    else:
        lines.append("🤖 Auto-generated by [Paper Hunter](https://github.com/MSWEIMZ/paper-hunter)")
    lines.append("")

    return "\n".join(lines)
