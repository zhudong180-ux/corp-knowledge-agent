"""三个工具的统一封装：search_docs / query_db / graph_lookup。

每个函数都是无状态、可独立测试、可被 MCP 暴露的纯函数。
"""
from __future__ import annotations

from functools import lru_cache

from src.graph_rag import GraphRAG
from src.nl2sql import NL2SQL
from src.rag import DocSearcher


@lru_cache(maxsize=1)
def _searcher() -> DocSearcher:
    return DocSearcher()


@lru_cache(maxsize=1)
def _nl2sql() -> NL2SQL:
    return NL2SQL()


@lru_cache(maxsize=1)
def _graph() -> GraphRAG:
    return GraphRAG()


def search_docs(query: str, top_k: int = 3) -> dict:
    """从公司政策文档中检索相关段落。"""
    chunks = _searcher().search(query, top_k=top_k)
    return {"chunks": chunks, "answer": "\n".join(c["text"] for c in chunks)}


def query_db(question: str) -> dict:
    """自然语言问题 → 查 SQLite 数据库。"""
    return _nl2sql().run(question)


def graph_lookup(question: str) -> dict:
    """在预抽取的知识图谱中查询实体和 N 跳关系。"""
    return _graph().lookup(question)


TOOL_REGISTRY = {
    "search_docs": search_docs,
    "query_db": query_db,
    "graph_lookup": graph_lookup,
}


def reset_tools_cache() -> None:
    """测试用：清掉 lru_cache 让重新初始化。"""
    _searcher.cache_clear()
    _nl2sql.cache_clear()
    _graph.cache_clear()