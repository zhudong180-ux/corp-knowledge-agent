"""LLM 单例：支持真实 OpenAI 兼容 API 与本地 mock 模式。"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config import get_settings


@dataclass
class LLMResponse:
    content: str


class MockLLM:
    """离线 mock：基于关键词返回固定答案，用于演示不依赖外网。"""

    def invoke(self, prompt: str) -> LLMResponse:
        p = prompt.lower()
        if "年假" in p:
            return LLMResponse(content="[mock] 年假规则：工作满 1 年 5 天，满 5 年 10 天。试用期员工按 50% 计算。")
        if "研发部" in p and ("入职" in p or "多少" in p):
            return LLMResponse(content="[mock] 上个月研发部入职 2 人：张三、李四。")
        if "张三" in p:
            return LLMResponse(content="[mock] 张三是研发部 P5 工程师，名下有 1 台 MacBook Pro。")
        if "select" in p or "sql" in p:
            return LLMResponse(content="SELECT COUNT(*) FROM employees WHERE dept_id = 1 AND hire_date >= date('now','-1 month');")
        return LLMResponse(content="[mock] 我是离线模式 LLM，未匹配到规则。建议切换 LLM_MODE=real。")


@lru_cache(maxsize=1)
def get_llm():
    s = get_settings()
    if s.llm_mode == "mock":
        return MockLLM()
    return ChatOpenAI(
        base_url=s.llm_base_url,
        api_key=s.llm_api_key,
        model=s.llm_model,
        temperature=0.0,
    )


def reset_llm_cache() -> None:
    """测试时用：清掉 lru_cache 让重新读 env。"""
    get_llm.cache_clear()