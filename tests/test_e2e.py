"""端到端：跑 data/test_questions.json 里所有问题，验证 expect_tools 命中。"""
from __future__ import annotations

import json
import os

import pytest

from src.agent import run_agent
from src.config import reset_settings_cache
from src.llm import reset_llm_cache
from src.tools import reset_tools_cache


@pytest.fixture(autouse=True)
def _force_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    monkeypatch.setenv("SQLITE_PATH", "./data/employees.db")
    reset_settings_cache()
    reset_llm_cache()
    reset_tools_cache()
    yield
    reset_settings_cache()
    reset_llm_cache()
    reset_tools_cache()


@pytest.fixture(scope="module")
def questions():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "test_questions.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("case", [
    {"q": "我们公司年假怎么算？", "expect_tools": ["search_docs"]},
    {"q": "研发部上个月入职了多少人？", "expect_tools": ["query_db"]},
    {"q": "张三名下有几台笔记本？", "expect_tools": ["query_db"]},
    {"q": "张三属于什么部门？", "expect_tools": ["graph_lookup"]},
    {"q": "申请新笔记本要走什么流程？", "expect_tools": ["search_docs"]},
])
def test_e2e_seed_question(case):
    r = run_agent(case["q"])
    assert r["answer"], "答案不能为空"
    assert any(t in r["tools_used"] for t in case["expect_tools"]), (
        f"期望工具 {case['expect_tools']}，实际 {r['tools_used']}"
    )