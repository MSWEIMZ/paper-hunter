"""趋势报告模块"""
from __future__ import annotations
from datetime import datetime
from collections import defaultdict


def _quarter_from_month(month: int) -> str:
    if month <= 3: return "Q1"
    elif month <= 6: return "Q2"
    elif month <= 9: return "Q3"
    else: return "Q4"


def generate_trends_markdown(records: list[dict]) -> str:
    """生成趋势报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["# 📈 论文趋势报告", "", f"> 生成时间: {now}", ""]

    # 按年统计
    by_year: dict[int, int] = defaultdict(int)
    for r in records:
        by_year[r.get("year", 0)] += 1

    if by_year:
        lines.append("## 📅 年度统计")
        lines.append("")
        lines.append("| 年份 | 论文数 | 趋势 |")
        lines.append("|------|--------|------|")
        prev_count = 0
        for year in sorted(by_year.keys()):
            count = by_year[year]
            trend = ""
            if prev_count > 0:
                change = ((count - prev_count) / prev_count) * 100
                if change > 10:
                    trend = f"📈 +{change:.0f}%"
                elif change < -10:
                    trend = f"📉 {change:.0f}%"
                else:
                    trend = "➡️ 持平"
            lines.append(f"| {year} | {count} | {trend} |")
            prev_count = count
        lines.append("")

    # 按季度统计（最近 2 年）
    by_quarter: dict[str, int] = defaultdict(int)
    for r in records:
        published = r.get("published", "")
        if published and len(published) >= 7:
            try:
                year = int(published[:4])
                month = int(published[5:7])
                q = f"{year} {_quarter_from_month(month)}"
                by_quarter[q] += 1
            except (ValueError, IndexError):
                pass

    if by_quarter:
        recent_quarters = sorted(by_quarter.keys())[-8:]
        lines.append("## 📊 季度趋势（最近 8 个季度）")
        lines.append("")
        lines.append("| 季度 | 论文数 |")
        lines.append("|------|--------|")
        for q in recent_quarters:
            lines.append(f"| {q} | {by_quarter[q]} |")
        lines.append("")

    # 热门主题 Top 10
    topic_counts: dict[str, int] = defaultdict(int)
    for r in records:
        for t in r.get("topics", []):
            topic_counts[t] += 1

    if topic_counts:
        top_topics = sorted(topic_counts.items(), key=lambda x: -x[1])[:10]
        lines.append("## 🔥 热门主题 Top 10")
        lines.append("")
        lines.append("| 主题 | 论文数 |")
        lines.append("|------|--------|")
        for topic, count in top_topics:
            lines.append(f"| {topic} | {count} |")
        lines.append("")

    return "\n".join(lines)
