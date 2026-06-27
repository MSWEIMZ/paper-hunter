"""通用论文相关性评分模块"""
from __future__ import annotations
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
