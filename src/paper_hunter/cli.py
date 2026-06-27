"""Paper Hunter — 通用论文搜集 CLI 入口"""
from __future__ import annotations
import sys
import json
from pathlib import Path
from datetime import datetime

from .config import load_profile, ProfileConfig, FilterConfig, ScoringConfig, RuntimeConfig, NotificationConfig
from .collector import collect_candidates
from .normalizer import build_paper_record, extract_year
from .scorer import compute_score, assign_label
from .storage import upsert_paper, get_all_records, get_stats, get_existing_ids
from .notify import send_notification
from .templates import TEMPLATES
from .sources_config import SourcesConfig, BuiltinSourceConfig, CustomSourceConfig
from .summarizer import enhance_record
from .topics import classify_paper_topics, generate_topics_markdown
from .trends import generate_trends_markdown
from .readme import generate_readme
from .dashboard import generate_dashboard_html
from .citation_filler import fill_citations


def run_daily(profile_path: str | Path) -> None:
    """每日搜集流程"""
    config = load_profile(profile_path)
    base = Path(profile_path).parent.parent

    # 加载数据源配置
    sources_path = base / "sources.json"
    if sources_path.exists():
        with sources_path.open("r", encoding="utf-8") as f:
            sources_raw = json.load(f)
        sources_config = _parse_sources_config(sources_raw)
    else:
        sources_config = SourcesConfig()
    output_dir = base / config.output_dir
    index_path = output_dir / "index.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Paper Hunter — {config.profile_name}")
    print("=" * 60)

    # 1. 收集候选
    print("\n[1/4] Collect candidates...")
    try:
        candidates = collect_candidates(config, sources_config)
    except Exception as e:
        print(f"  [ERROR] 搜索失败: {e}")
        send_notification(
            config.profile_name, [], {},
            config.notification.webhook_env, [str(e)],
        )
        return

    if not candidates:
        print("  无候选论文，退出")
        return

    # 2. 评分过滤
    print("\n[2/4] Score and filter...")
    existing_ids = get_existing_ids(index_path)
    new_records: list[dict] = []
    noise_blocked = 0

    for query_type, search_query, raw_paper in candidates:
        published = raw_paper.get("published", "")
        arxiv_id = raw_paper.get("arxiv_id", "")
        year = extract_year(published, arxiv_id)
        if year < config.filters.years_from or year > config.filters.years_to:
            continue

        categories = raw_paper.get("categories", [])
        allowed = set(config.filters.allowed_categories)
        if categories and not any(c in allowed for c in categories):
            if not any(c.startswith("cs.") for c in categories):
                continue

        score = compute_score(
            raw_paper, query_type, search_query,
            blocked_keywords=config.filters.blocked_keywords,
            domain_keywords=config.domain_keywords,
            config=config.scoring,
        )
        label = assign_label(
            score,
            min_score=config.scoring.min_relevance_score,
            core_threshold=config.scoring.core_threshold,
        )
        if label == "noise":
            noise_blocked += 1
            continue

        record = build_paper_record(raw_paper, query_type, search_query)
        record.relevance_score = score
        record.quality_label = label
        new_records.append(record.to_dict())

    print(f"  通过: {len(new_records)}, 噪声过滤: {noise_blocked}")

    # 3. 写入索引
    print("\n[3/4] Write index...")
    added = 0
    updated = 0
    for rec in new_records:
        is_new = upsert_paper(index_path, rec)
        if is_new:
            added += 1
        else:
            updated += 1
    print(f"  新增: {added}, 更新: {updated}")

    # 3.5 增强记录
    print("\n[3.5/5] Enhance records...")
    all_records = get_all_records(index_path)
    for rec in all_records:
        rec = enhance_record(rec)
        rec["topics"] = classify_paper_topics(rec)
        upsert_paper(index_path, rec)

    # 3.6 生成显示文件
    print("\n[3.6/5] Generate display files...")
    stats = get_stats(index_path)
    stats["noise_blocked_today"] = noise_blocked

    # README
    readme_content = generate_readme(all_records, stats, config.profile_name, config.description)
    (output_dir / "README.md").write_text(readme_content, encoding="utf-8")

    # Topics
    topics_content = generate_topics_markdown(all_records)
    (output_dir / "TOPICS.md").write_text(topics_content, encoding="utf-8")

    # Trends
    trends_content = generate_trends_markdown(all_records)
    (output_dir / "TRENDS.md").write_text(trends_content, encoding="utf-8")

    # Dashboard
    dashboard_content = generate_dashboard_html(all_records, stats, config.profile_name)
    (output_dir / "dashboard.html").write_text(dashboard_content, encoding="utf-8")

    print("  README/TOPICS/TRENDS/dashboard.html 已生成")

    # 4. 通知
    print("\n[5/5] Notify...")
    all_records = get_all_records(index_path)
    stats = get_stats(index_path)
    stats["noise_blocked_today"] = noise_blocked

    if config.notification.type == "feishu":
        send_notification(
            config.profile_name, new_records, stats,
            config.notification.webhook_env,
        )

    print(f"\n[DONE] added={added} updated={updated} noise_blocked={noise_blocked}")
    print(f"  输出目录: {output_dir}")


def run_init() -> None:
    """交互式初始化向导"""
    print("\n🎯 Paper Hunter 初始化向导")
    print("=" * 40)

    # Step 1: 选择模板
    print("\n第 1 步：选择研究领域\n")
    template_keys = list(TEMPLATES.keys())
    for i, key in enumerate(template_keys, 1):
        tmpl = TEMPLATES[key]
        print(f"  {i}) {tmpl['name']}")
    print(f"  {len(template_keys) + 1}) 自定义")

    choice = input(f"\n请选择 [1-{len(template_keys) + 1}]: ").strip()

    if choice == str(len(template_keys) + 1):
        # 自定义
        profile_name = input("\n研究领域名称: ").strip()
        if not profile_name:
            print("❌ 名称不能为空")
            return
        template_data = None
    else:
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(template_keys):
                raise ValueError
            template_key = template_keys[idx]
            template_data = TEMPLATES[template_key]
            profile_name = template_data["name"]
            print(f"\n✅ 已选择：{profile_name}")
        except (ValueError, IndexError):
            print("❌ 无效选择")
            return

    # Step 2: 核心关键词
    print("\n第 2 步：核心关键词（可修改，直接回车使用默认）\n")
    if template_data:
        default_queries = template_data["core_queries"]
        print("默认关键词：")
        for q in default_queries:
            print(f"  - {q}")
        user_input = input("\n直接回车使用默认，或输入自定义关键词（逗号分隔）:\n> ").strip()
        if user_input:
            core_queries = [q.strip() for q in user_input.split(",") if q.strip()]
        else:
            core_queries = default_queries
            print("\n✅ 使用默认关键词")
    else:
        print("请输入核心关键词（逗号分隔）:")
        user_input = input("> ").strip()
        core_queries = [q.strip() for q in user_input.split(",") if q.strip()]
        if not core_queries:
            print("❌ 至少需要一个关键词")
            return

    # Step 3: 扩展关键词
    print("\n第 3 步：扩展关键词（可选，直接回车跳过）\n")
    if template_data:
        default_expanded = template_data["expanded_queries"]
        print("默认扩展关键词：")
        for q in default_expanded:
            print(f"  - {q}")
        user_input = input("\n直接回车使用默认，或输入自定义（逗号分隔）:\n> ").strip()
        if user_input:
            expanded_queries = [q.strip() for q in user_input.split(",") if q.strip()]
        else:
            expanded_queries = default_expanded
    else:
        print("请输入扩展关键词（逗号分隔，直接回车跳过）:")
        user_input = input("> ").strip()
        expanded_queries = [q.strip() for q in user_input.split(",") if q.strip()] if user_input else []

    # Step 4: 飞书 Webhook
    print("\n第 4 步：飞书通知（可选）\n")
    webhook_url = input("请输入飞书 Webhook URL（直接回车跳过）:\n> ").strip()
    webhook_env = ""
    if webhook_url:
        webhook_env = "FEISHU_WEBHOOK"
        print("\n✅ 已配置飞书通知")
        print(f"   请设置环境变量：export FEISHU_WEBHOOK=\"{webhook_url}\"")

    # Step 5: 年份范围
    print("\n第 5 步：年份范围\n")
    years_from = input("起始年份 [2020]: ").strip() or "2020"
    years_to = input("结束年份 [2027]: ").strip() or "2027"
    try:
        years_from = int(years_from)
        years_to = int(years_to)
    except ValueError:
        print("❌ 无效年份，使用默认值")
        years_from = 2020
        years_to = 2027
    print(f"\n✅ 年份范围：{years_from}-{years_to}")

    # Step 6: 数据源
    print("\n第 6 步：搜索数据源\n")
    print("  1) arXiv（推荐，速度快）")
    print("  2) Semantic Scholar（引用数据更全）")
    print("  3) 两者都用（覆盖更广，但更慢）")
    source_choice = input("\n请选择 [1-3] (默认 1): ").strip() or "1"
    source_map = {"1": ["arxiv"], "2": ["semantic_scholar"], "3": ["arxiv", "semantic_scholar"]}
    source_labels = {"1": "arXiv", "2": "Semantic Scholar", "3": "arXiv + Semantic Scholar"}
    sources = source_map.get(source_choice, ["arxiv"])
    source_label = source_labels.get(source_choice, "arXiv")
    print(f"\n✅ 数据源：{source_label}")

    # Step 7: 搜索时间
    print("\n第 7 步：每天搜索时间\n")
    print("  1) 早上 8:00")
    print("  2) 中午 12:00")
    print("  3) 晚上 20:00")
    print("  4) 自定义")
    time_choice = input("\n请选择 [1-4] (默认 1): ").strip() or "1"
    time_map = {"1": "0 0 * * *", "2": "0 4 * * *", "3": "0 12 * * *"}
    if time_choice in time_map:
        cron_schedule = time_map[time_choice]
        time_labels = {"1": "早上 8:00 (北京时间)", "2": "中午 12:00 (北京时间)", "3": "晚上 20:00 (北京时间)"}
        time_label = time_labels[time_choice]
    else:
        hour = input("  小时 (0-23): ").strip()
        minute = input("  分钟 (0-59): ").strip() or "0"
        try:
            hour = int(hour)
            minute = int(minute)
            # 北京时间转 UTC (减 8 小时)
            utc_hour = (hour - 8) % 24
            cron_schedule = f"{minute} {utc_hour} * * *"
            time_label = f"{hour}:{minute:02d} (北京时间)"
        except ValueError:
            cron_schedule = "0 0 * * *"
            time_label = "早上 8:00 (北京时间)"
    print(f"\n✅ 搜索时间：{time_label}")

    # 生成配置
    if template_data:
        domain_keywords = template_data["domain_keywords"]
        exploratory_queries = template_data["exploratory_queries"]
        description = template_data["description"]
    else:
        domain_keywords = []
        exploratory_queries = []
        description = f"{profile_name} 论文自动搜集"

    config = {
        "profile_name": profile_name,
        "description": description,
        "output_dir": f"output/{profile_name.lower().replace(' ', '_')}",
        "queries": {
            "core": core_queries,
            "expanded": expanded_queries,
            "exploratory": exploratory_queries,
        },
        "domain_keywords": domain_keywords,
        "filters": {
            "years_from": years_from,
            "years_to": years_to,
            "allowed_categories": ["cs.CV", "cs.LG", "cs.AI"],
            "blocked_keywords": [],
        },
        "scoring": {
            "min_relevance_score": 2.5,
            "core_threshold": 4.0,
            "strongly_related_threshold": 2.5,
        },
        "notification": {
            "type": "feishu" if webhook_env else "none",
            "webhook_env": webhook_env,
        },
        "runtime": {
            "max_results_per_query": 30,
            "write_markdown_cards": True,
            "write_readme": True,
        },
        "schedule": {
            "cron": cron_schedule,
            "description": time_label,
        },
    }

    # 保存数据源配置
    sources_path = Path("sources.json")
    with sources_path.open("w", encoding="utf-8") as f:
        json.dump(sources_config, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 数据源配置已保存: {sources_path}")

    # 保存配置
    profiles_dir = Path("profiles")
    profiles_dir.mkdir(exist_ok=True)
    filename = profile_name.lower().replace(" ", "_").replace("/", "_") + ".json"
    profile_path = profiles_dir / filename

    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 40}")
    print(f"✅ 配置已生成: {profile_path}")

    print(f"\n📋 下一步：")
    print(f"   1. git add {profile_path} sources.json")
    print(f'   2. git commit -m "add {profile_name} profile"')
    print(f"   3. git push")
    print(f"   4. GitHub Actions 将每天自动运行")

    if webhook_env:
        print(f"\n🔔 飞书通知：")
        print(f'   export FEISHU_WEBHOOK="{webhook_url}"')

    print(f"\n⏰ 搜索时间：{time_label}")
    print(f"\n🎯 完成！")


def _parse_sources_config(raw: dict) -> SourcesConfig:
    """解析数据源配置"""
    builtin_raw = raw.get("builtin", {})
    builtin = {}
    for name, cfg in builtin_raw.items():
        builtin[name] = BuiltinSourceConfig(
            enabled=cfg.get("enabled", True),
            max_results=cfg.get("max_results", 30),
        )

    custom_raw = raw.get("custom", [])
    custom = []
    for cfg in custom_raw:
        custom.append(CustomSourceConfig(
            name=cfg.get("name", ""),
            enabled=cfg.get("enabled", True),
            api_url=cfg.get("api_url", ""),
            query_param=cfg.get("query_param", "q"),
            format=cfg.get("format", "json"),
            title_field=cfg.get("title_field", "title"),
            abstract_field=cfg.get("abstract_field", "abstract"),
            max_results=cfg.get("max_results", 20),
            headers=cfg.get("headers", {}),
        ))

    return SourcesConfig(builtin=builtin, custom=custom)


def run_backfill(profile_path: str | Path) -> None:
    """回填引用数据"""
    config = load_profile(profile_path)
    base = Path(profile_path).parent.parent
    output_dir = base / config.output_dir
    index_path = output_dir / "index.jsonl"

    print("=" * 60)
    print(f"Backfill — {config.profile_name}")
    print("=" * 60)

    if not index_path.exists():
        print("  [ERROR] index.jsonl 不存在，请先运行 run-daily")
        return

    all_records = get_all_records(index_path)
    print(f"  已有论文: {len(all_records)}")

    enriched, updated_records = fill_citations(all_records, max_fill=200)

    # 写回索引
    for rec in updated_records:
        upsert_paper(index_path, rec)

    print(f"\n[DONE] 回填 {enriched} 篇论文的引用数据")


def run_stats(profile_path: str | Path) -> None:
    """查看统计信息"""
    config = load_profile(profile_path)
    base = Path(profile_path).parent.parent
    output_dir = base / config.output_dir
    index_path = output_dir / "index.jsonl"

    print("=" * 60)
    print(f"Stats — {config.profile_name}")
    print("=" * 60)

    if not index_path.exists():
        print("  [ERROR] index.jsonl 不存在")
        return

    all_records = get_all_records(index_path)
    stats = get_stats(index_path)

    print(f"\n论文总数: {stats['total']}")
    print(f"\n按标签:")
    for label, count in stats.get("by_label", {}).items():
        print(f"  {label}: {count}")

    print(f"\n按年份:")
    for year, count in sorted(stats.get("by_year", {}).items(), reverse=True)[:10]:
        print(f"  {year}: {count}")

    cit_count = sum(1 for r in all_records if r.get("citation_count", 0) > 0)
    print(f"\n有引用数据: {cit_count}/{stats['total']}")


def run_export(profile_path: str | Path) -> None:
    """导出 BibTeX"""
    config = load_profile(profile_path)
    base = Path(profile_path).parent.parent
    output_dir = base / config.output_dir
    index_path = output_dir / "index.jsonl"

    if not index_path.exists():
        print("  [ERROR] index.jsonl 不存在")
        return

    all_records = get_all_records(index_path)
    bib_path = output_dir / "papers.bib"

    lines = []
    for r in all_records:
        if r.get("quality_label") not in ("core", "strongly_related"):
            continue

        cid = r.get("canonical_id", "unknown").replace(".", "").replace("/", "")
        title = r.get("title", "")
        authors = " and ".join(r.get("authors", []))
        year = r.get("year", "")
        url = r.get("url", "")
        venue = r.get("venue", "")
        abstract = r.get("abstract", "")[:200]

        entry = f"@article{{{cid},\n"
        entry += f"  title = {{{title}}},\n"
        entry += f"  author = {{{authors}}},\n"
        entry += f"  year = {{{year}}},\n"
        if venue:
            entry += f"  journal = {{{venue}}},\n"
        if url:
            entry += f"  url = {{{url}}},\n"
        if abstract:
            entry += f"  abstract = {{{abstract}}},\n"
        entry += "}\n"
        lines.append(entry)

    bib_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ BibTeX 已导出: {bib_path}")
    print(f"  共 {len(lines)} 条记录")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m paper_hunter.cli <command> [args]")
        print()
        print("Commands:")
        print("  init              交互式初始化向导")
        print("  run-daily <profile>  运行每日搜集")
        sys.exit(1)

    command = sys.argv[1]
    if command == "init":
        run_init()
    elif command == "run-daily":
        if len(sys.argv) < 3:
            print("Usage: python -m paper_hunter.cli run-daily <profile.json>")
            sys.exit(1)
        run_daily(sys.argv[2])
    elif command == "run-backfill":
        if len(sys.argv) < 3:
            print("Usage: python -m paper_hunter.cli run-backfill <profile.json>")
            sys.exit(1)
        run_backfill(sys.argv[2])
    elif command == "run-stats":
        if len(sys.argv) < 3:
            print("Usage: python -m paper_hunter.cli run-stats <profile.json>")
            sys.exit(1)
        run_stats(sys.argv[2])
    elif command == "run-export":
        if len(sys.argv) < 3:
            print("Usage: python -m paper_hunter.cli run-export <profile.json>")
            sys.exit(1)
        run_export(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print()
        print("Available commands:")
        print("  init              交互式初始化向导")
        print("  run-daily <profile>  运行每日搜集")
        print("  run-backfill <profile>  回填引用数据")
        print("  run-stats <profile>  查看统计信息")
        print("  run-export <profile>  导出 BibTeX")
        sys.exit(1)


if __name__ == "__main__":
    main()
