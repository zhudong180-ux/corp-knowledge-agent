import os

import pytest

from src.agent import (
    plan,
    reflect,
    route_by_llm,
    route_by_rule,
    run_agent,
)
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


def test_route_year_leave():
    assert route_by_rule("年假怎么算") == "search_docs"


def test_route_count_employees():
    assert route_by_rule("研发部上个月入职多少人") == "query_db"


def test_route_belong_to():
    assert route_by_rule("张三属于什么部门") == "graph_lookup"


def test_route_unknown_falls_back_to_llm():
    assert route_by_llm("随便问问") in {"search_docs", "query_db", "graph_lookup"}


def test_plan_returns_single_subtask_in_mock():
    p = plan("年假怎么算", "search_docs")
    assert isinstance(p, list)
    assert len(p) >= 1
    assert p[0]["tool"] == "search_docs"


def test_reflect_empty_chunks_returns_false():
    ok, sugg = reflect("年假怎么算", "search_docs", {"chunks": [], "answer": ""})
    assert ok is False
    assert sugg


def test_run_agent_returns_full_result():
    r = run_agent("我们公司年假怎么算？")
    assert "answer" in r
    assert "tools_used" in r
    assert len(r["steps"]) >= 1
    assert r["intent"] == "search_docs"


def test_run_agent_db_route():
    r = run_agent("研发部上个月入职多少人？")
    assert r["intent"] == "query_db"
    assert "query_db" in r["tools_used"]