"""数据源配置模块"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BuiltinSourceConfig:
    """内置数据源配置"""
    enabled: bool = True
    max_results: int = 30


@dataclass
class CustomSourceConfig:
    """自定义数据源配置"""
    name: str = ""
    enabled: bool = True
    api_url: str = ""
    query_param: str = "q"
    format: str = "json"  # json / xml
    title_field: str = "title"
    abstract_field: str = "abstract"
    authors_field: str = "authors"
    url_field: str = "url"
    max_results: int = 20
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class SourcesConfig:
    """数据源总配置"""
    builtin: dict[str, BuiltinSourceConfig] = field(default_factory=lambda: {
        "arxiv": BuiltinSourceConfig(enabled=True, max_results=30),
        "semantic_scholar": BuiltinSourceConfig(enabled=False, max_results=20),
        "openalex": BuiltinSourceConfig(enabled=False, max_results=20),
        "crossref": BuiltinSourceConfig(enabled=False, max_results=20),
    })
    custom: list[CustomSourceConfig] = field(default_factory=list)
