"""FastMCP server：把 search_docs / query_db / graph_lookup 暴露成 MCP 工具。

启动：python -m src.mcp_server
默认 stdio 传输；任何 MCP 兼容 client 都能调用。
"""
from __future__ import annotations

import sys


def main():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print("缺少依赖：fastmcp。请运行 pip install fastmcp>=0.4.0", file=sys.stderr)
        sys.exit(1)

    from src.tools import graph_lookup, query_db, search_docs

    mcp = FastMCP("corp-knowledge-agent")

    @mcp.tool()
    def search_docs_tool(query: str, top_k: int = 3) -> dict:
        """从公司政策文档（HR/IT/报销/入职）中检索相关段落。

        Args:
            query: 检索关键词，如「年假怎么算」
            top_k: 返回条数，默认 3

        Returns:
            {"chunks": [{"text": ..., "source": ..., "score": ...}], "answer": ...}
        """
        return search_docs(query, top_k=top_k)

    @mcp.tool()
    def query_db_tool(question: str) -> dict:
        """自然语言问题 → 查员工/部门/资产数据库。

        Args:
            question: 自然语言问题，如「研发部上个月入职多少人」

        Returns:
            {"sql": ..., "rows": [...], "answer": ...}
        """
        return query_db(question)

    @mcp.tool()
    def graph_lookup_tool(question: str) -> dict:
        """在知识图谱中查询实体和 N 跳关系。

        Args:
            question: 自然语言问题，如「张三属于什么部门」

        Returns:
            {"entity": ..., "path": [...], "answer": ...}
        """
        return graph_lookup(question)

    mcp.run()


if __name__ == "__main__":
    main()