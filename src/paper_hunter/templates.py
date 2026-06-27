"""预设模板数据"""
from __future__ import annotations

TEMPLATES: dict[str, dict] = {
    "video": {
        "name": "视频理解与分析",
        "description": "视频深度学习、动作识别、视频理解相关论文",
        "core_queries": [
            "video understanding deep learning",
            "action recognition neural network",
            "3D CNN video classification",
            "spatiotemporal convolution video",
            "video temporal reasoning",
        ],
        "expanded_queries": [
            "video transformer",
            "video feature extraction",
            "video representation learning",
            "SlowFast TimeSformer VideoMAE",
            "video action recognition benchmark",
        ],
        "exploratory_queries": [
            "video foundation model",
            "video multimodal learning",
            "video generation",
        ],
        "domain_keywords": [
            "video", "action recognition", "3D CNN", "spatiotemporal",
            "temporal", "SlowFast", "TimeSformer", "VideoMAE",
        ],
    },
    "vision": {
        "name": "计算机视觉",
        "description": "图像识别、目标检测、图像分割等计算机视觉论文",
        "core_queries": [
            "image classification deep learning",
            "object detection neural network",
            "image segmentation",
            "visual recognition",
        ],
        "expanded_queries": [
            "image generation",
            "visual question answering",
            "scene understanding",
            "visual reasoning",
        ],
        "exploratory_queries": [
            "vision transformer",
            "vision foundation model",
            "multimodal vision language",
        ],
        "domain_keywords": [
            "image", "visual", "detection", "segmentation",
            "recognition", "CNN", "vision",
        ],
    },
    "nlp": {
        "name": "自然语言处理",
        "description": "文本分类、机器翻译、问答系统等 NLP 论文",
        "core_queries": [
            "natural language processing",
            "text classification",
            "machine translation",
            "question answering",
            "sentiment analysis",
        ],
        "expanded_queries": [
            "named entity recognition",
            "text summarization",
            "information extraction",
            "dialogue system",
        ],
        "exploratory_queries": [
            "language model",
            "prompt engineering",
            "instruction tuning",
        ],
        "domain_keywords": [
            "text", "language", "NLP", "transformer",
            "BERT", "GPT", "token",
        ],
    },
    "llm": {
        "name": "大语言模型",
        "description": "LLM、提示工程、指令微调等大模型论文",
        "core_queries": [
            "large language model",
            "LLM",
            "instruction tuning",
            "prompt engineering",
            "chain of thought",
        ],
        "expanded_queries": [
            "retrieval augmented generation",
            "RLHF",
            "alignment",
            "safety",
            "benchmark",
        ],
        "exploratory_queries": [
            "multimodal LLM",
            "agent",
            "reasoning",
            "planning",
        ],
        "domain_keywords": [
            "LLM", "language model", "GPT", "LLaMA",
            "instruction", "prompt", "alignment",
        ],
    },
    "medical": {
        "name": "医学影像",
        "description": "医学图像分析、临床诊断 AI 等论文",
        "core_queries": [
            "medical image segmentation",
            "medical image classification",
            "clinical decision support",
            "radiology AI",
            "pathology image analysis",
        ],
        "expanded_queries": [
            "medical image registration",
            "medical image synthesis",
            "healthcare NLP",
            "electronic health record",
        ],
        "exploratory_queries": [
            "multimodal medical",
            "clinical trial",
            "drug discovery",
        ],
        "domain_keywords": [
            "medical", "clinical", "radiology", "pathology",
            "healthcare", "diagnosis", "imaging",
        ],
    },
    "robotics": {
        "name": "机器人学习",
        "description": "机器人控制、强化学习、操作等论文",
        "core_queries": [
            "robot learning",
            "robot manipulation",
            "reinforcement learning robot",
            "imitation learning",
            "robot control",
        ],
        "expanded_queries": [
            "sim to real transfer",
            "robot navigation",
            "grasping",
            "locomotion",
        ],
        "exploratory_queries": [
            "embodied AI",
            "robot foundation model",
            "humanoid robot",
        ],
        "domain_keywords": [
            "robot", "manipulation", "reinforcement learning",
            "control", "grasping", "navigation",
        ],
    },
    "diffusion": {
        "name": "扩散模型",
        "description": "扩散模型、图像生成、视频生成等论文",
        "core_queries": [
            "diffusion model",
            "denoising diffusion",
            "image generation",
            "text to image",
            "stable diffusion",
        ],
        "expanded_queries": [
            "video generation",
            "3D generation",
            "image editing",
            "inpainting",
        ],
        "exploratory_queries": [
            "diffusion policy",
            "diffusion transformer",
            "flow matching",
        ],
        "domain_keywords": [
            "diffusion", "generation", "denoising",
            "stable diffusion", "DALL-E", "Midjourney",
        ],
    },
    "xai": {
        "name": "可解释 AI",
        "description": "模型可解释性、可视化、归因方法等论文",
        "core_queries": [
            "explainable AI",
            "model interpretability",
            "Grad-CAM",
            "saliency map",
            "feature visualization",
        ],
        "expanded_queries": [
            "attention visualization",
            "SHAP LIME",
            "concept bottleneck",
            "network dissection",
        ],
        "exploratory_queries": [
            "mechanistic interpretability",
            "probing",
            "representation analysis",
        ],
        "domain_keywords": [
            "explainable", "interpretable", "saliency",
            "Grad-CAM", "attention", "visualization", "XAI",
        ],
    },
}
