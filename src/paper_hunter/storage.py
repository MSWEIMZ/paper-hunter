"""JSONL 索引存储模块"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime


def _load_index(index_path: Path) -> dict[str, dict]:
    """加载索引，返回 {canonical_id: record}"""
    records: dict[str, dict] = {}
    if not index_path.exists():
        return records
    with index_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                cid = rec.get("canonical_id", "")
                if cid:
                    records[cid] = rec
            except json.JSONDecodeError:
                continue
    return records


def _save_index(index_path: Path, records: dict[str, dict]) -> None:
    """将索引写回 JSONL，按年份降序、分数降序排列"""
    sorted_recs = sorted(
        records.values(),
        key=lambda r: (-r.get("year", 0), -r.get("relevance_score", 0)),
    )
    with index_path.open("w", encoding="utf-8") as f:
        for rec in sorted_recs:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_index(index_path: str | Path) -> dict[str, dict]:
    """公开接口：加载索引"""
    return _load_index(Path(index_path))


def upsert_paper(index_path: str | Path, record: dict) -> bool:
    """插入或更新论文，返回 True 表示新增"""
    p = Path(index_path)
    records = _load_index(p)
    cid = record.get("canonical_id", "")
    if not cid:
        return False

    is_new = cid not in records
    existing = records.get(cid, {})

    new_ver = record.get("version", 1)
    old_ver = existing.get("version", 0)
    if new_ver >= old_ver:
        if not is_new and old_ver > 0:
            history = existing.get("version_history", [])
            history.append({"version": old_ver, "updated": existing.get("updated", "")})
            record["version_history"] = history[-10:]
        records[cid] = record
    else:
        history = existing.get("version_history", [])
        history.append({"version": new_ver, "updated": record.get("updated", "")})
        existing["version_history"] = history[-10:]
        records[cid] = existing

    p.parent.mkdir(parents=True, exist_ok=True)
    _save_index(p, records)
    return is_new


def get_existing_ids(index_path: str | Path) -> set[str]:
    """返回索引中所有 canonical_id"""
    return set(_load_index(Path(index_path)).keys())


def get_all_records(index_path: str | Path) -> list[dict]:
    """返回所有记录，按年份降序、分数降序"""
    records = _load_index(Path(index_path))
    return sorted(
        records.values(),
        key=lambda r: (-r.get("year", 0), -r.get("relevance_score", 0)),
    )


def get_stats(index_path: str | Path) -> dict:
    """返回索引统计信息"""
    records = _load_index(Path(index_path))
    by_label: dict[str, int] = {}
    by_year: dict[int, int] = {}
    for rec in records.values():
        label = rec.get("quality_label", "unknown")
        by_label[label] = by_label.get(label, 0) + 1
        year = rec.get("year", 0)
        by_year[year] = by_year.get(year, 0) + 1
    return {
        "total": len(records),
        "by_label": by_label,
        "by_year": dict(sorted(by_year.items(), reverse=True)),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
