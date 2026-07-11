"""通用配置加载模块"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FilterConfig:
    years_from: int = 2015
    years_to: int = 2027
    allowed_categories: list[str] = field(default_factory=lambda: ["cs.CV", "cs.LG", "cs.AI"])
    blocked_keywords: list[str] = field(default_factory=list)


@dataclass
class ScoringConfig:
    min_relevance_score: float = 2.5
    core_threshold: float = 4.0
    strongly_related_threshold: float = 2.5
    keyword_weights: dict[str, float] = field(default_factory=lambda: {
        "core": 2.0, "expanded": 1.0, "exploratory": 0.5
    })
    category_bonus: dict[str, float] = field(default_factory=lambda: {
        "cs.CV": 1.0, "cs.LG": 0.5, "cs.AI": 0.3
    })
    survey_bonus: float = 0.8
    venue_bonus: dict[str, float] = field(default_factory=lambda: {
        "CVPR": 0.5, "ICCV": 0.5, "ECCV": 0.5,
        "NeurIPS": 0.4, "ICML": 0.4, "ICLR": 0.4, "AAAI": 0.3,
    })
    citation_bonus_threshold: int = 50
    citation_bonus: float = 0.5
    blocked_penalty: float = 10.0
    top_k: int = 5


@dataclass
class RuntimeConfig:
    max_results_per_query: int = 30
    write_markdown_cards: bool = True
    write_readme: bool = True


@dataclass
class NotificationConfig:
    type: str = "none"  # none / feishu / telegram / email
    webhook_env: str = ""  # 飞书 webhook 环境变量名
    telegram_token_env: str = ""  # Telegram Bot Token 环境变量名
    telegram_chat_env: str = ""  # Telegram Chat ID 环境变量名
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password_env: str = "SMTP_PASSWORD"
    to_email: str = ""


@dataclass
class ScheduleConfig:
    cron: str = "0 0 * * *"
    description: str = "早上 8:00 (北京时间)"


@dataclass
class ProfileConfig:
    profile_name: str = ""
    description: str = ""
    output_dir: str = "papers"
    core_queries: list[str] = field(default_factory=list)
    expanded_queries: list[str] = field(default_factory=list)
    exploratory_queries: list[str] = field(default_factory=list)
    domain_keywords: list[str] = field(default_factory=list)
    filters: FilterConfig = field(default_factory=FilterConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)

    def to_dict(self) -> dict:
        """序列化为 dict"""
        return {
            "profile_name": self.profile_name,
            "description": self.description,
            "output_dir": self.output_dir,
            "queries": {
                "core": self.core_queries,
                "expanded": self.expanded_queries,
                "exploratory": self.exploratory_queries,
            },
            "domain_keywords": self.domain_keywords,
            "filters": {
                "years_from": self.filters.years_from,
                "years_to": self.filters.years_to,
                "allowed_categories": self.filters.allowed_categories,
                "blocked_keywords": self.filters.blocked_keywords,
            },
            "scoring": {
                "min_relevance_score": self.scoring.min_relevance_score,
                "core_threshold": self.scoring.core_threshold,
                "strongly_related_threshold": self.scoring.strongly_related_threshold,
            },
            "notification": {
                "type": self.notification.type,
                "webhook_env": self.notification.webhook_env,
            },
        }


def load_profile(path: str | Path) -> ProfileConfig:
    """加载 profile JSON 并返回 ProfileConfig"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Profile 不存在: {p}")

    with p.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    # 校验必填字段
    if not raw.get("profile_name"):
        raise ValueError("配置缺少 profile_name")
    queries = raw.get("queries", {})
    if not queries.get("core"):
        raise ValueError("配置缺少 queries.core")

    # Filters
    f_raw = raw.get("filters", {})
    filters = FilterConfig(
        years_from=f_raw.get("years_from", 2015),
        years_to=f_raw.get("years_to", 2027),
        allowed_categories=f_raw.get("allowed_categories", ["cs.CV", "cs.LG", "cs.AI"]),
        blocked_keywords=f_raw.get("blocked_keywords", []),
    )

    # Scoring
    s_raw = raw.get("scoring", {})
    scoring = ScoringConfig(
        min_relevance_score=s_raw.get("min_relevance_score", 2.5),
        core_threshold=s_raw.get("core_threshold", 4.0),
        strongly_related_threshold=s_raw.get("strongly_related_threshold", 2.5),
        top_k=s_raw.get("top_k", 5),
    )

    # Runtime
    r_raw = raw.get("runtime", {})
    runtime = RuntimeConfig(
        max_results_per_query=r_raw.get("max_results_per_query", 30),
        write_markdown_cards=r_raw.get("write_markdown_cards", True),
        write_readme=r_raw.get("write_readme", True),
    )

    # Notification
    n_raw = raw.get("notification", {})
    notification = NotificationConfig(
        type=n_raw.get("type", "none"),
        webhook_env=n_raw.get("webhook_env", ""),
        telegram_token_env=n_raw.get("telegram_token_env", ""),
        telegram_chat_env=n_raw.get("telegram_chat_env", ""),
        smtp_host=n_raw.get("smtp_host", ""),
        smtp_port=n_raw.get("smtp_port", 587),
        smtp_user=n_raw.get("smtp_user", ""),
        smtp_password_env=n_raw.get("smtp_password_env", "SMTP_PASSWORD"),
        to_email=n_raw.get("to_email", ""),
    )

    # Schedule
    sched_raw = raw.get("schedule", {})
    schedule = ScheduleConfig(
        cron=sched_raw.get("cron", "0 0 * * *"),
        description=sched_raw.get("description", ""),
    )

    return ProfileConfig(
        profile_name=raw["profile_name"],
        description=raw.get("description", ""),
        output_dir=raw.get("output_dir", "papers"),
        core_queries=queries.get("core", []),
        expanded_queries=queries.get("expanded", []),
        exploratory_queries=queries.get("exploratory", []),
        domain_keywords=raw.get("domain_keywords", []),
        filters=filters,
        scoring=scoring,
        runtime=runtime,
        notification=notification,
        schedule=schedule,
    )
