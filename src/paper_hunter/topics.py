"""主题聚类模块 - 通用关键词聚类"""
from __future__ import annotations
from collections import defaultdict


# 通用主题定义（可通过 profile 配置覆盖）
DEFAULT_TOPIC_DEFINITIONS: dict[str, dict] = {
    "deep_learning": {
        "name": "Deep Learning",
        "name_cn": "深度学习",
        "keywords": ["deep learning", "neural network", "CNN", "RNN", "LSTM", "transformer"],
        "description": "深度学习基础方法",
    },
    "generative_models": {
        "name": "Generative Models",
        "name_cn": "生成模型",
        "keywords": ["generative", "GAN", "VAE", "diffusion", "generation", "synthesis"],
        "description": "生成对抗网络、变分自编码器、扩散模型等",
    },
    "nlp": {
        "name": "Natural Language Processing",
        "name_cn": "自然语言处理",
        "keywords": ["NLP", "language model", "text", "BERT", "GPT", "LLM", "transformer"],
        "description": "自然语言处理相关",
    },
    "computer_vision": {
        "name": "Computer Vision",
        "name_cn": "计算机视觉",
        "keywords": ["image", "visual", "detection", "segmentation", "recognition", "classification"],
        "description": "图像识别、目标检测、图像分割等",
    },
    "interpretability": {
        "name": "Interpretability",
        "name_cn": "可解释性",
        "keywords": ["explainable", "interpretable", "saliency", "Grad-CAM", "attention", "visualization", "XAI"],
        "description": "模型可解释性与可视化",
    },
    "reinforcement_learning": {
        "name": "Reinforcement Learning",
        "name_cn": "强化学习",
        "keywords": ["reinforcement learning", "RL", "policy", "reward", "agent", "MDP"],
        "description": "强化学习相关",
    },
    "optimization": {
        "name": "Optimization",
        "name_cn": "优化",
        "keywords": ["optimization", "efficient", "compression", "pruning", "quantization", "distillation"],
        "description": "模型优化、压缩、加速",
    },
    "multimodal": {
        "name": "Multimodal",
        "name_cn": "多模态",
        "keywords": ["multimodal", "vision-language", "CLIP", "cross-modal", "VQA"],
        "description": "多模态学习",
    },
    "medical_ai": {
        "name": "Medical AI",
        "name_cn": "医学 AI",
        "keywords": ["medical", "clinical", "radiology", "pathology", "healthcare", "diagnosis"],
        "description": "医学影像与临床 AI",
    },
    "robotics": {
        "name": "Robotics",
        "name_cn": "机器人学",
        "keywords": ["robot", "manipulation", "navigation", "grasping", "locomotion", "embodied"],
        "description": "机器人学习与控制",
    },
    "survey_benchmark": {
        "name": "Survey & Benchmark",
        "name_cn": "综述与基准",
        "keywords": ["survey", "review", "benchmark", "taxonomy", "comparison", "evaluation"],
        "description": "综述论文与基准测试",
    },
}


def classify_paper_topics(record: dict, topic_defs: dict[str, dict] | None = None) -> list[str]:
    """为论文分配主题标签

    Args:
        record: 论文记录
        topic_defs: 主题定义（可选，默认使用通用定义）

    Returns:
        命中的主题 ID 列表
    """
    if topic_defs is None:
        topic_defs = DEFAULT_TOPIC_DEFINITIONS

    text = f"{record.get('title', '')} {record.get('abstract', '')}".lower()
    topics = []

    for topic_id, topic_info in topic_defs.items():
        keywords = topic_info.get("keywords", [])
        if any(kw.lower() in text for kw in keywords):
            topics.append(topic_id)

    return topics


def generate_topics_markdown(records: list[dict], topic_defs: dict[str, dict] | None = None) -> str:
    """生成主题统计 Markdown"""
    if topic_defs is None:
        topic_defs = DEFAULT_TOPIC_DEFINITIONS

    topic_counts: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        topics = r.get("topics", [])
        for t in topics:
            topic_counts[t].append(r)

    lines = ["# 📊 主题统计", ""]

    for topic_id in sorted(topic_counts.keys(), key=lambda t: -len(topic_counts[t])):
        topic_info = topic_defs.get(topic_id, {})
        name = topic_info.get("name", topic_id)
        name_cn = topic_info.get("name_cn", "")
        desc = topic_info.get("description", "")
        papers = topic_counts[topic_id]

        lines.append(f"## {name} ({name_cn}) - {len(papers)} 篇")
        if desc:
            lines.append(f"> {desc}")
        lines.append("")

        # Top 5 论文
        for p in papers[:5]:
            title = p.get("title", "")[:60]
            url = p.get("url", "#")
            lines.append(f"- [{title}]({url})")
        if len(papers) > 5:
            lines.append(f"- ... 还有 {len(papers) - 5} 篇")
        lines.append("")

    return "\n".join(lines)
