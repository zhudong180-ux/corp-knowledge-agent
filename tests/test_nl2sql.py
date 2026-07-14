import os
import tempfile

import pytest

from data.seed_db import build_seed_db
from src.config import reset_settings_cache
from src.llm import reset_llm_cache
from src.nl2sql import NL2SQL, sql_is_safe


@pytest.fixture(autouse=True)
def _force_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    reset_settings_cache()
    reset_llm_cache()
    yield
    reset_settings_cache()
    reset_llm_cache()


def test_sql_is_safe_accepts_select():
    assert sql_is_safe("SELECT * FROM employees") is True


def test_sql_is_safe_rejects_drop():
    assert sql_is_safe("DROP TABLE employees") is False


def test_sql_is_safe_rejects_delete():
    assert sql_is_safe("DELETE FROM employees") is False


def test_sql_is_safe_rejects_insert():
    assert sql_is_safe("INSERT INTO employees VALUES (1)") is False


def test_nl2sql_mock_mode_returns_results():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        build_seed_db(db)
        engine = NL2SQL(db_path=db, mode="mock")
        result = engine.run("研发部上个月入职多少人")
        assert "rows" in result
        assert "answer" in result
        assert "sql" in result


def test_nl2sql_zhang_san_assets():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        build_seed_db(db)
        engine = NL2SQL(db_path=db, mode="mock")
        result = engine.run("张三名下有几台笔记本")
        assert "MacBook" in str(result["rows"]) or len(result["rows"]) >= 1


def test_nl2sql_count_query():
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "test.db")
        build_seed_db(db)
        engine = NL2SQL(db_path=db, mode="mock")
        result = engine.run("全公司多少人")
        assert result["rows"][0].get("total", 0) >= 20