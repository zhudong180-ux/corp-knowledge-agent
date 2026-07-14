"""Jinja2 Prompt 加载器：支持参数渲染。"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.config import project_root


@lru_cache(maxsize=1)
def _env() -> Environment:
    prompts_dir = project_root() / "prompts"
    return Environment(
        loader=FileSystemLoader(str(prompts_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(name: str, **kwargs) -> str:
    """加载 prompts/<name>.jinja 并渲染。"""
    template = _env().get_template(f"{name}.jinja")
    return template.render(**kwargs)