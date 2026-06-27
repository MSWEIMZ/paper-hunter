"""Paper Hunter — 通用论文搜集 CLI 入口"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime

from .config import load_profile
from .collector import collect_candidates
from .normalizer import build_paper_record, extract_year
from .scorer import compute_score, assign_label
from .storage import upsert_paper, get_all_records, get_stats, get_existing_ids
from .notify import send_notification


def run_daily(profile_path: str | Path) -> None:
    """每日搜集流程"""
    config = load_profile(profile_path)
    base = Path(profile_path).parent.parent
    output_dir = base / config.output_dir
    index_path = output_dir / "index.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"Paper Hunter — {config.profile_name}")
    print("=" * 60)

    # 1. 收集候选
    print("\n[1/4] Collect candidates...")
    try:
        candidates = collect_candidates(config)
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

    # 4. 通知
    print("\n[4/4] Notify...")
    all_records = get_all_records(index_path)
    stats = get_stats(index_path)
    stats["noise_blocked_today"] = noise_blocked

    if config.notification.type == "feishu":
        send_notification(
            config.profile_name, new_records, stats,
            config.notification.webhook_env,
        )

    print(f"\n[DONE] added={added} updated={updated} noise_blocked={noise_blocked}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python -m paper_hunter.cli run-daily <profile.json>")
        print("       python -m paper_hunter.cli list-profiles")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run-daily":
        run_daily(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
