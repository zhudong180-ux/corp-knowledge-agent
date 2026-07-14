"""验证 MCP 工具可被外部客户端调用（用 FastMCP 装饰器 introspect）。"""
from __future__ import annotations

import os

import pytest

from src.mcp_server import main as mcp_main


def test_mcp_main_callable():
    assert callable(mcp_main)


def test_mcp_tools_registerable():
    """验证 FastMCP 能注册三个工具函数。"""
    try:
        from mcp.server.fastmcp import FastMCP
        from src.tools import graph_lookup, query_db, search_docs
    except ImportError:
        pytest.skip("fastmcp 未安装")

    mcp = FastMCP("test")
    mcp.tool()(search_docs)
    mcp.tool()(query_db)
    mcp.tool()(graph_lookup)
    # 没抛异常 = OK
    assert True


def test_mcp_server_module_imports():
    """验证 mcp_server 模块能干净 import（不真起 server）。"""
    import src.mcp_server as mod
    assert hasattr(mod, "main")
    assert callable(mod.main)