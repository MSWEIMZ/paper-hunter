"""日志模块"""
from __future__ import annotations
import logging
import sys
from pathlib import Path


def setup_logger(name: str = "paper_hunter", log_file: str | Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """配置日志

    Args:
        name: 日志名称
        log_file: 日志文件路径（可选）
        level: 日志级别

    Returns:
        Logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# 全局 logger
logger = setup_logger()
