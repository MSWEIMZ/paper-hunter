"""通用论文相关性评分模块"""
from __future__ import annotations
import math
from datetime import datetime
from .config import ScoringConfig


# 顶级会议加分表
_TOP_TIER_VENUES: dict[str, float] = {
    "cvpr": 0.5, "iccv": 0.5, "eccv": 0.5,
    "neurips": 0.4, "nips": 0.4, "icml": 0.4, "iclr": 0.4,
    "aaai": 0.3, "ijcai": 0.3, "emnlp": 0.3, "acl": 0.3,
    "siggraph": 0.5, "mm": 0.3, "acm mm": 0.3,
    "miccai": 0.4, "ismrm": 0.3,  # 医学影像
    "nature": 0.5, "science": 0.5, "cell": 0.4,  # 顶刊
}

# 综述关键词
_SURVEY_KEYWORDS: list[str] = [
    "survey", "review", "benchmark", "taxonomy", "comprehensive review",
    "systematic review", "meta-analysis", "comparative study",
]


def _text_contains(text: str, keywords: list[str]) -> list[str]:
    """返回 text 中命中的关键词列表"""
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def _detect_venue_bonus(venue_text: str, venue_bonuses: dict[str, float] | None = None) -> float:
    """从 venue 文本中检测顶级会议并返回加分"""
    if venue_bonuses is None:
        venue_bonuses = _TOP_TIER_VENUES
    text_lower = venue_text.lower()
    best_bonus = 0.0
    for venue, bonus in venue_bonuses.items():
        if venue in text_lower:
            best_bonus = max(best_bonus, bonus)
    return best_bonus


def _detect_survey_bonus(text: str) -> float:
    """检测综述关键词"""
    text_lower = text.lower()
    if any(kw in text_lower for kw in _SURVEY_KEYWORDS):
        return 0.8
    return 0.0


def compute_score(
    paper: dict,
    query_type: str,
    search_query: str,
    blocked_keywords: list[str] | None = None,
    domain_keywords: list[str] | None = None,
    config: ScoringConfig | None = None,
) -> float:
    """计算论文相关性分数

    Args:
        paper: 原始论文 dict
        query_type: 查询类型 (core/expanded/exploratory)
        search_query: 搜索关键词
        blocked_keywords: 屏蔽关键词列表
        domain_keywords: 域关键词列表（命中加分）
        config: 评分配置

    Returns:
        相关性分数（可为负数）
    """
    if config is None:
        config = ScoringConfig()

    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    text = f"{title} {abstract}".lower()
    score = 0.0

    # 1. 屏蔽关键词检查
    if blocked_keywords:
        if any(kw.lower() in text for kw in blocked_keywords):
            return -config.blocked_penalty

    # 2. 查询类型基础分
    score += config.keyword_weights.get(query_type, 0.5)

    # 3. 搜索关键词命中
    query_words = [w.strip().lower() for w in search_query.split() if len(w.strip()) > 2]
    hits = sum(1 for w in query_words if w in text)
    if query_words:
        hit_ratio = hits / len(query_words)
        score += hit_ratio * 2.0

    # 4. 域关键词加分
    if domain_keywords:
        domain_hits = sum(1 for kw in domain_keywords if kw.lower() in text)
        score += domain_hits * 0.3

    # 5. 会议加分
    venue = paper.get("venue", "")
    if venue:
        venue_bonus = _detect_venue_bonus(venue)
        # 也用配置中的 venue_bonus
        if config.venue_bonus:
            venue_bonus = max(venue_bonus, _detect_venue_bonus(venue, config.venue_bonus))
        score += venue_bonus

    # 6. 综述加分
    score += _detect_survey_bonus(text)

    # 7. 引用量加分
    citation_count = paper.get("citation_count", 0)
    if citation_count >= config.citation_bonus_threshold:
        score += config.citation_bonus

    # 8. 类别加分
    categories = paper.get("categories", [])
    if categories and config.category_bonus:
        best_cat_bonus = max(
            (config.category_bonus.get(c, 0.0) for c in categories),
            default=0.0,
        )
        score += best_cat_bonus

    return round(score, 2)


def assign_label(
    score: float,
    min_score: float = 2.5,
    core_threshold: float = 4.0,
) -> str:
    """根据分数分配质量标签"""
    if score >= core_threshold:
        return "core"
    if score >= min_score:
        return "strongly_related"
    return "noise"


def compute_novelty_score(year: int, current_year: int | None = None) -> float:
    """计算新颖性分数 (0.0 - 1.0)

    当前年份 = 1.0，每老一年衰减 20%，最低 0.0
    """
    if current_year is None:
        current_year = datetime.now().year
    age = max(0, current_year - year)
    if age == 0:
        return 1.0
    if age == 1:
        return 0.8
    # 指数衰减
    score = max(0.0, 1.0 - age * 0.15)
    return round(score, 2)


def compute_impact_score(citation_count: int) -> float:
    """计算影响力分数 (0.0 - 1.0)

    使用对数归一化：log10(citations + 1) / log10(10000)
    10000 引用 => 1.0，100 引用 => 0.5，10 引用 => 0.25
    """
    if citation_count <= 0:
        return 0.0
    score = math.log10(citation_count + 1) / math.log10(10001)
    return round(min(1.0, score), 2)


def compute_hotness_score(
    citation_count: int,
    citations_recent: list[int] | None = None,
) -> float:
    """计算热度分数 (0.0 - 1.0)

    如果有近期引用数据 (最近几个月的引用数)，用近期引用 / 总引用的比率。
    如果没有近期数据，用总引用的对数作为热度估算。
    """
    if citations_recent and len(citations_recent) > 0:
        recent_total = sum(citations_recent)
        if citation_count > 0:
            # 近期引用占比，越高越热
            ratio = recent_total / max(citation_count, 1)
            # 加上近期引用的绝对量
            recent_avg = recent_total / len(citations_recent)
            score = min(1.0, ratio * 0.5 + math.log10(recent_avg + 1) / 3.0)
            return round(score, 2)
    # 无近期数据，用总引用估算
    if citation_count <= 0:
        return 0.0
    score = math.log10(citation_count + 1) / 5.0
    return round(min(1.0, score), 2)


def compute_multi_dimension_score(
    paper: dict,
    relevance: float,
    current_year: int | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """计算多维度综合评分

    Args:
        paper: 论文记录
        relevance: 相关性分数（已计算好的）
        current_year: 当前年份
        weights: 各维度权重，默认 relevance:0.4, novelty:0.2, impact:0.25, hotness:0.15

    Returns:
        {"relevance": float, "novelty": float, "impact": float, "hotness": float, "composite": float}
    """
    if weights is None:
        weights = {"relevance": 0.4, "novelty": 0.2, "impact": 0.25, "hotness": 0.15}

    year = paper.get("year", 2020)
    citation_count = paper.get("citation_count", 0)
    citations_recent = paper.get("citations_recent", [])

    novelty = compute_novelty_score(year, current_year)
    impact = compute_impact_score(citation_count)
    hotness = compute_hotness_score(citation_count, citations_recent)

    # 归一化 relevance 到 0-1 范围（假设最大 10 分）
    relevance_norm = min(1.0, max(0.0, relevance / 10.0))

    composite = (
        weights["relevance"] * relevance_norm
        + weights["novelty"] * novelty
        + weights["impact"] * impact
        + weights["hotness"] * hotness
    )
    # 还原到 relevance 的量级（乘以 10）
    composite_score = round(composite * 10.0, 2)

    return {
        "relevance": round(relevance, 2),
        "novelty": novelty,
        "impact": impact,
        "hotness": hotness,
        "composite": composite_score,
    }
