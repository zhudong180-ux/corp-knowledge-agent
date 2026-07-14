"""全局配置加载：使用 pydantic-settings 从 .env 读取。"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_mode: str = Field(default="real", description="real | mock")
    llm_base_url: str = Field(default="https://api.deepseek.com/v1")
    llm_api_key: str = Field(default="")
    llm_model: str = Field(default="deepseek-chat")

    # Embedding
    embed_model: str = Field(default="paraphrase-multilingual-MiniLM-L12-v2")

    # 路径
    data_dir: str = Field(default="./data")
    docs_dir: str = Field(default="./data/docs")
    sqlite_path: str = Field(default="./data/employees.db")
    graph_path: str = Field(default="./data/graph.json")

    # Agent 行为
    max_react_steps: int = Field(default=3)
    max_reflections: int = Field(default=2)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def project_root() -> Path:
    """返回项目根目录（agent-demo/）。"""
    return Path(__file__).resolve().parent.parent


def reset_settings_cache() -> None:
    """测试时用：清掉 lru_cache 让重新读 env。"""
    get_settings.cache_clear()