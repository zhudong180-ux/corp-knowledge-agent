import os
import shutil
import tempfile

import pytest

from src.rag import DocSearcher


@pytest.fixture(scope="module")
def searcher():
    """模块级 fixture：跑一次 doc 加载 + embedding（首次会下载 ~120MB）。"""
    s = DocSearcher(persist_dir=tempfile.mkdtemp(prefix="rag_test_"))
    s._ensure_loaded()
    return s


def test_search_returns_chunks_about_year_leave(searcher):
    results = searcher.search("年假怎么算", top_k=3)
    assert len(results) > 0
    assert any("年假" in r["text"] for r in results)


def test_search_chunks_have_metadata(searcher):
    results = searcher.search("年假", top_k=1)
    assert "source" in results[0]
    assert "score" in results[0]
    assert results[0]["source"].endswith(".md")


def test_search_expense(searcher):
    results = searcher.search("出差到北京住宿能报多少", top_k=2)
    assert len(results) > 0
    assert any("800" in r["text"] or "住宿" in r["text"] for r in results)


def test_search_returns_at_most_top_k(searcher):
    results = searcher.search("笔记本", top_k=2)
    assert len(results) <= 2