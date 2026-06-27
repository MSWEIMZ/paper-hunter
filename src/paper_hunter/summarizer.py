"""摘要增强模块 - 基于规则的一句话摘要与方法类型检测"""
from __future__ import annotations


# 方法关键词表
METHOD_KEYWORDS: dict[str, list[str]] = {
    "gradient-based": ["grad-cam", "gradient", "backpropagation", "saliency map", "integrated gradient", "smoothgrad"],
    "attention-based": ["attention", "self-attention", "cross-attention", "transformer", "attention rollout"],
    "perturbation-based": ["perturbation", "occlusion", "lime", "rise", "ablation"],
    "probing": ["probing", "probe", "linear classifier", "representation analysis", "feature visualization"],
    "concept-based": ["concept", "concept bottleneck", "network dissection", "tcav"],
    "generative": ["generative", "generation", "diffusion", "gan", "vae", "synthesis"],
    "benchmark": ["benchmark", "dataset", "evaluation", "survey", "review", "taxonomy"],
    "visualization": ["visualization", "visualize", "feature map", "activation map", "heatmap"],
    "classification": ["classification", "recognition", "detection", "segmentation"],
    "optimization": ["optimization", "efficient", "acceleration", "compression", "pruning", "quantization"],
}


def _extract_first_sentences(text: str, max_chars: int = 200) -> str:
    """提取前 1-2 句话"""
    if not text:
        return ""
    sentences = text.replace("\n", " ").split(".")
    result = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if result:
            result += ". " + s
        else:
            result = s
        if len(result) >= max_chars:
            break
    return result.strip() + "." if result and not result.endswith(".") else result


def detect_method_type(text: str) -> str:
    """检测论文方法类型"""
    text_lower = text.lower()
    hits: list[tuple[str, int]] = []
    for method, keywords in METHOD_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0:
            hits.append((method, count))
    if not hits:
        return "other"
    hits.sort(key=lambda x: -x[1])
    return hits[0][0]


def generate_one_line_summary(record: dict) -> str:
    """生成一句话摘要（英文）"""
    abstract = record.get("abstract", "")
    if not abstract:
        return record.get("title", "")[:100]
    return _extract_first_sentences(abstract, 150)


def generate_summary_zh(record: dict) -> str:
    """生成中文摘要（基于规则的简单翻译/提取）

    注意：这是一个基于规则的简单实现，不依赖外部 API。
    对于更好的中文摘要，可以接入翻译 API。
    """
    abstract = record.get("abstract", "")
    if not abstract:
        return record.get("title", "")[:80]

    # 提取前 2 句话
    summary = _extract_first_sentences(abstract, 200)

    # 如果已经有中文摘要，直接返回
    if any('\u4e00' <= c <= '\u9fff' for c in summary):
        return summary[:80]

    # 简单截断作为摘要
    return summary[:80] + "..." if len(summary) > 80 else summary


def enhance_record(record: dict) -> dict:
    """增强论文记录（添加摘要、方法类型等）"""
    text = f"{record.get('title', '')} {record.get('abstract', '')}"

    # 一句话摘要
    if not record.get("one_line_summary"):
        record["one_line_summary"] = generate_one_line_summary(record)

    # 中文摘要
    if not record.get("summary_zh"):
        record["summary_zh"] = generate_summary_zh(record)

    # 方法类型
    if not record.get("method_type"):
        record["method_type"] = detect_method_type(text)

    return record
