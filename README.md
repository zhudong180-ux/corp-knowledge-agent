# corp-knowledge-agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://langchain-ai.github.io/langgraph/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.12-orange)](https://www.llamaindex.ai/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.4-purple)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-42%2F42%20passing-brightgreen)](tests/)
[![Code lines](https://img.shields.io/badge/code-~2000%20lines-blue)](src/)

> 企业知识库工具项目，覆盖 JD **Graph RAG、NL2SQL、ReAct/Reflection、MCP、LangGraph、LlamaIndex、Prompt 工程** 7 个关键词。

## 它能做什么

项目工具集。

业务场景：虚构「极星科技」公司的内部助理，员工可以问：

```text
我们公司年假怎么算？试用期的员工呢？            →  RAG + Reflection
研发部上个月入职了多少人？分别是谁？            →  NL2SQL
张三是研发部的吗？他适用什么制度？有什么资产？  →  Graph RAG + 多工具融合
```

## 安装指导

```bash
git clone https://github.com/zhudong180-ux/corp-knowledge-agent.git
cd corp-knowledge-agent
pip install -r requirements.txt
python -m data.seed_db                # 初始化 SQLite
bash demo/run_all.sh                  # 一键跑完三个问题（mock 模式）
```

接真 LLM（DeepSeek 示例）：
```bash
echo "LLM_MODE=real" > .env
echo "LLM_BASE_URL=https://api.deepseek.com/v1" >> .env
echo "LLM_API_KEY=sk-your-key" >> .env
echo "LLM_MODEL=deepseek-chat" >> .env
bash demo/run_all.sh real
```

## 技术亮点

| 能力 | 实现 | 主文件 |
|---|---|---|
| **Graph RAG** | NetworkX + 中文实体抽取 + N 跳扩展 | [`src/graph_rag.py`](src/graph_rag.py) |
| **NL2SQL** | LLM 生成 + SQL 安全白名单（只允许 SELECT） | [`src/nl2sql.py`](src/nl2sql.py) |
| **ReAct / Reflection** | LangGraph 状态机 + 反思触发自动换工具重试 | [`src/agent.py`](src/agent.py) |
| **MCP 工具调用** | FastMCP 暴露三个工具为 MCP 标准协议 | [`src/mcp_server.py`](src/mcp_server.py) |
| **LangGraph** | Router → Planner → ReAct → Synthesizer | [`src/agent.py`](src/agent.py) |
| **LlamaIndex** | 文档加载 + ChromaDB + 本地 HF embedding | [`src/rag.py`](src/rag.py) |
| **Prompt 工程** | 5 个 jinja 模块化模板 + few-shot | [`prompts/`](prompts/) |

## 演示输出示例（mock 模式）

```
问题 #1: 我们公司年假怎么算？试用期的员工呢？
[意图] search_docs
[工具] search_docs
  step1. search_docs(...) → 员工年假按工作年限累计...
→ 回答：年假规则：工作满 1 年 5 天，满 5 年 10 天...

问题 #2: 研发部上个月入职了多少人？分别是谁？
[意图] query_db
[工具] query_db
  step1. query_db(...) → 共 1 条记录：郑十一

问题 #3: 张三是研发部的吗？他适用什么制度？有什么资产？
[意图] graph_lookup
[工具] graph_lookup
  step1. graph_lookup(...) → 找到实体：员工:张三 → 部门:研发部...
```

## 目录结构

```
corp-knowledge-agent/
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── data/              # 文档 + SQLite + 知识图谱
├── prompts/           # 5 个 Prompt 模板（jinja）
├── src/               # 核心代码（agent / tools / mcp_server / ...）
├── tests/             # 42 个测试
└── demo/              # 一键演示脚本 + 讲解稿
```

## 测试覆盖

```bash
pytest tests/ -v
```

**42/42 测试全绿** — config 3 + llm 3 + seed_db 4 + rag 4 + nl2sql 7 + graph_rag 5 + agent 8 + e2e 5 + mcp 3

## JD 关键词 → 文件映射

| JD 关键词 | 主文件 | 关键函数 / 类 |
|---|---|---|
| Graph RAG | `src/graph_rag.py` | `GraphRAG.lookup()` |
| NL2SQL | `src/nl2sql.py` | `NL2SQL.run()`, `sql_is_safe()` |
| ReAct / Reflection | `src/agent.py` | `react_loop_node()`, `reflect()` |
| MCP 工具调用 | `src/mcp_server.py` | `FastMCP("corp-knowledge-agent")` |
| LangGraph | `src/agent.py` | `build_graph()`, `AgentState` |
| LlamaIndex | `src/rag.py` | `DocSearcher.search()` |
| Prompt 工程 | `prompts/*.jinja` + `src/prompts.py` | 5 个模块化模板 |

## 设计取舍

1. **Router 用规则 + LLM 兜底** —— 现场可以讲「轻量路由」的设计哲学
2. **ReAct 循环最多 3 步** —— 避免死循环，可调试
3. **Embedding 本地跑** —— `paraphrase-multilingual-MiniLM-L12-v2`（~120MB，本地 CPU < 50ms）
4. **LLM 走 OpenAI 兼容协议** —— DeepSeek / OpenAI / MiniMax 一行 .env 切换
5. **离线 mock 模式** —— `LLM_MODE=mock` 完全不依赖外网也能跑完

## 现场稳定性

- **mock 模式** (`LLM_MODE=mock`)：完全不依赖外部 API、跑通全部流程
- **本地 embedding**：sentence-transformers / paraphrase-multilingual-MiniLM-L12-v2
- **LLM 可切**：DeepSeek / OpenAI / MiniMax 都走 OpenAI 兼容协议
- **网络抖动回退**：mock 模式可兜底

## 后续扩展（YAGNI 清单，本期不做）

- 多用户会话管理
- 文档自动更新（CI 拉新文档重抽取图谱）
- Coze/Dify 平台对接
- 前端 UI（Gradio/Streamlit）
- 流式输出

## License

MIT