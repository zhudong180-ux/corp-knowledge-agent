import os

import pytest

from src.config import reset_settings_cache
from src.llm import MockLLM, get_llm, reset_llm_cache


@pytest.fixture(autouse=True)
def _force_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    reset_settings_cache()
    reset_llm_cache()
    yield
    reset_settings_cache()
    reset_llm_cache()


def test_get_llm_returns_object(monkeypatch):
    reset_llm_cache()
    monkeypatch.setenv("LLM_MODE", "mock")
    llm = get_llm()
    assert llm is not None
    assert hasattr(llm, "invoke")
    reset_llm_cache()


def test_mock_llm_responds():
    llm = MockLLM()
    out = llm.invoke("你好")
    assert out.content
    assert "mock" in out.content.lower() or len(out.content) > 0


def test_mock_llm_year_leave():
    llm = MockLLM()
    out = llm.invoke("我们公司年假怎么算？")
    assert "年假" in out.content