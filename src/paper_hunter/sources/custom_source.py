"""自定义数据源通用搜索模块"""
from __future__ import annotations
import json
import time
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.parse import urlencode, quote

from ..sources_config import CustomSourceConfig


def _get_nested_value(data: dict, field_path: str) -> str:
    """从嵌套 dict 中按路径提取值

    例如: "data.title" -> data["data"]["title"]
    """
    keys = field_path.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, "")
        elif isinstance(value, list) and key.isdigit():
            idx = int(key)
            value = value[idx] if idx < len(value) else ""
        else:
            return ""
    return str(value) if value else ""


def _parse_json_response(data: str, config: CustomSourceConfig) -> list[dict]:
    """解析 JSON 响应"""
    try:
        root = json.loads(data)
    except json.JSONDecodeError:
        return []

    # 如果是列表，直接使用
    if isinstance(root, list):
        items = root
    # 如果是对象，尝试提取 results/items/data 字段
    elif isinstance(root, dict):
        items = root.get("results", root.get("items", root.get("data", [])))
        if isinstance(items, dict):
            items = [items]
    else:
        return []

    papers = []
    for item in items[:config.max_results]:
        title = _get_nested_value(item, config.title_field)
        if not title:
            continue

        abstract = _get_nested_value(item, config.abstract_field) if config.abstract_field else ""
        authors_str = _get_nested_value(item, config.authors_field) if config.authors_field else ""
        url = _get_nested_value(item, config.url_field) if config.url_field else ""

        # 解析作者
        if isinstance(authors_str, list):
            authors = [str(a) for a in authors_str[:5]]
        elif authors_str:
            authors = [a.strip() for a in authors_str.split(",")[:5]]
        else:
            authors = ["Unknown"]

        papers.append({
            "title": title.strip(),
            "authors": authors,
            "summary": abstract.strip(),
            "url": url,
            "arxiv_url": "",
            "arxiv_id": "",
            "published": "",
            "updated": "",
            "pdf_url": "",
            "categories": [],
            "primary_category": "",
            "journal_ref": "",
            "citation_count": 0,
            "venue": "",
            "source": f"custom:{config.name}",
        })

    return papers


def _parse_xml_response(data: str, config: CustomSourceConfig) -> list[dict]:
    """解析 XML 响应"""
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return []

    papers = []
    # 尝试找到所有可能的条目元素
    for item in root.iter():
        if item.tag in ("hit", "entry", "item", "result", "record"):
            title = ""
            abstract = ""
            authors = ["Unknown"]
            url = ""

            for child in item:
                tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                text = child.text or ""

                if tag in ("title", config.title_field):
                    title = text
                elif tag in ("abstract", config.abstract_field):
                    abstract = text
                elif tag in ("authors", config.authors_field):
                    authors = [a.strip() for a in text.split(",")[:5]]
                elif tag in ("url", "link", config.url_field):
                    url = text

            if title:
                papers.append({
                    "title": title.strip(),
                    "authors": authors,
                    "summary": abstract.strip(),
                    "url": url,
                    "arxiv_url": "",
                    "arxiv_id": "",
                    "published": "",
                    "updated": "",
                    "pdf_url": "",
                    "categories": [],
                    "primary_category": "",
                    "journal_ref": "",
                    "citation_count": 0,
                    "venue": "",
                    "source": f"custom:{config.name}",
                })

            if len(papers) >= config.max_results:
                break

    return papers


def search_custom_source(query: str, config: CustomSourceConfig) -> list[dict]:
    """搜索自定义数据源

    Args:
        query: 搜索关键词
        config: 自定义数据源配置

    Returns:
        论文列表
    """
    if not config.enabled or not config.api_url:
        return []

    # 构建 URL
    params = {config.query_param: query}
    url = f"{config.api_url}?{urlencode(params)}"

    # 发送请求
    try:
        headers = {"User-Agent": "paper-hunter/1.0"}
        headers.update(config.headers)
        req = Request(url, headers=headers)
        with urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8")
    except Exception as e:
        print(f"  [WARN] 自定义源 {config.name} 请求失败: {e}")
        return []

    # 解析响应
    if config.format == "json":
        papers = _parse_json_response(data, config)
    elif config.format == "xml":
        papers = _parse_xml_response(data, config)
    else:
        print(f"  [WARN] 不支持的格式: {config.format}")
        return []

    time.sleep(0.5)  # 速率限制
    return papers
