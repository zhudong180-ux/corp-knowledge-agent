# corp-knowledge-agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)](https://langchain-ai.github.io/langgraph/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.12-orange)](https://www.llamaindex.ai/)
[![FastMCP](https://img.shields.io/badge/FastMCP-0.4-purple)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-42%2F42%20passing-brightgreen)](tests/)
[![Code lines](https://img.shields.io/badge/code-~2000%20lines-blue)](src/)

> 一个能现场 15 分钟演示完整闭环的「企业知识库智能体」演示项目，
> 覆盖 JD 中 **Graph RAG、NL2SQL、ReAct/Reflection、MCP、LangGraph、LlamaIndex、Prompt 工程** 7 个关键词。

## ✨ 它能做什么

一个能跑、能讲故事、能用代码回答任何追问的智能体演示项目。**让面试官在 15 分钟内看到一个完整智能体的运行**。

业务场景：虚构「极星科技」公司的内部助理，员工可以问：

```text
我们公司年假怎么算？试用期的员工呢？            →  RAG + Reflection
研发部上个月入职了多少人？分别是谁？            →  NL2SQL
张三是研发部的吗？他适用什么制度？有什么资产？  →  Graph RAG + 多工具融合
```

## 🚀 30 秒上手

```bash
git clone https://github.com/zhudong180-ux/corp-knowledge-agent.git
cd corp-knowledge-agent
pip install -r requirements.txt
python -m data.seed_db                # 初始化 SQLite
bash demo/run_all.sh                  # 一键跑完三个杀手问题（mock 模式）
```

接真 LLM（DeepSeek 示例）：
```bash
echo "LLM_MODE=real" > .env
echo "LLM_BASE_URL=https://api.deepseek.com/v1" >> .env
echo "LLM_API_KEY=sk-your-key" >> .env
echo "LLM_MODEL=deepseek-chat" >> .env
bash demo/run_all.sh real
```

## 🧠 技术亮点

| 能力 | 实现 | 主文件 |
|---|---|---|
| **Graph RAG** | NetworkX + 中文实体抽取 + N 跳扩展 | [`src/graph_rag.py`](src/graph_rag.py) |
| **NL2SQL** | LLM 生成 + SQL 安全白名单（只允许 SELECT） | [`src/nl2sql.py`](src/nl2sql.py) |
| **ReAct / Reflection** | LangGraph 状态机 + 反思触发自动换工具重试 | [`src/agent.py`](src/agent.py) |
| **MCP 工具调用** | FastMCP 暴露三个工具为 MCP 标准协议 | [`src/mcp_server.py`](src/mcp_server.py) |
| **LangGraph** | Router → Planner → ReAct → Synthesizer | [`src/agent.py`](src/agent.py) |
| **LlamaIndex** | 文档加载 + ChromaDB + 本地 HF embedding | [`src/rag.py`](src/rag.py) |
| **Prompt 工程** | 5 个 jinja 模块化模板 + few-shot | [`prompts/`](prompts/) |

## 🎬 15 分钟面试演示脚本

按时间段标注，每段都有「做什么」「说什么」「打开哪个文件」。详见 [`demo/questions.md`](demo/questions.md)。

```
[0:00-1:00]   开场 + 项目全景
[1:00-4:30]   Q1 年假（RAG + Reflection）
[4:30-7:00]   Q2 研发部入职人数（NL2SQL）
[7:00-9:30]   Q3 张三画像（Graph + DB 融合）
[9:30-12:00]  MCP 工具调用
[12:00-13:30] Prompt 工程与框架选型
[13:30-14:30] 测试 + 性能
[14:30-15:00] 收尾
```

## 📁 目录结构

```
corp-knowledge-agent/
├── README.md          ← 你正在看
├── LICENSE
├── requirements.txt
├── .env.example
├── data/              # 文档 + SQLite + 知识图谱
├── prompts/           # 5 个模块化 Prompt 模板（jinja）
├── src/               # 核心代码（agent/tools/mcp_server/...）
├── tests/             # 42 个测试
└── demo/              # 一键演示脚本 + 15 分钟讲解稿
```

## ✅ 测试覆盖

```bash
pytest tests/ -v
```

**42/42 测试全绿** — config 3 + llm 3 + seed_db 4 + rag 4 + nl2sql 7 + graph_rag 5 + agent 8 + e2e 5 + mcp 3

## 🎯 设计取舍

1. **Router 用规则 + LLM 兜底** —— 现场可以讲「轻量路由」的设计哲学
2. **ReAct 循环最多 3 步** —— 避免死循环，可调试
3. **Embedding 本地跑** —— `paraphrase-multilingual-MiniLM-L12-v2`（~120MB，本地 CPU < 50ms）
4. **LLM 走 OpenAI 兼容协议** —— DeepSeek / OpenAI / MiniMax 一行 .env 切换
5. **离线 mock 模式** —— `LLM_MODE=mock` 完全不依赖外网也能跑完

## 项目目标

构建一个中等体量（~2000 行）、能现场跑、能讲故事、能用代码回答任何追问的智能体演示项目。
不是工程完备，而是**让面试官在 15 分钟内看到一个完整智能体的运行**。

## 业务场景

虚构「极星科技」公司的内部助理，员工可以问：
- 「我们公司年假怎么算？试用期的员工呢？」（RAG + Reflection）
- 「研发部上个月入职了多少人？分别是谁？」（NL2SQL）
- 「张三是研发部的吗？他适用什么制度？有什么资产？」（Graph RAG + 多工具融合）

## 目录结构

```
agent-demo/
├── README.md                  ← 你正在看
├── requirements.txt
├── .env.example
├── data/
│   ├── docs/                  # 4 份 Markdown 政策文档
│   ├── employees.db           # SQLite（30 员工 + 20 资产 + 5 部门）
│   ├── graph.json             # 知识图谱（21 节点 + 18 边）
│   ├── seed_db.py             # 数据库初始化
│   └── test_questions.json    # 5 个种子问答对
├── prompts/                   # 模块化 Prompt 模板（jinja）
│   ├── router.jinja           # 意图路由
│   ├── planner.jinja          # 任务拆解
│   ├── nl2sql.jinja           # SQL 生成（含 few-shot）
│   ├── reflect.jinja          # 反思检查
│   └── synthesize.jinja       # 答案整合
├── src/
│   ├── config.py              # pydantic 配置
│   ├── llm.py                 # LLM 单例（real + mock 双模式）
│   ├── prompts.py             # jinja loader
│   ├── rag.py                 # LlamaIndex 文档检索
│   ├── nl2sql.py              # NL → SQL → 执行（含安全白名单）
│   ├── graph_rag.py           # NetworkX 图查询
│   ├── tools.py               # 三个工具的 Python 封装
│   ├── tools_cli.py           # 独立测试工具用 CLI
│   ├── mcp_server.py          # FastMCP server
│   ├── agent.py               # LangGraph 状态机
│   └── main.py                # CLI 入口
├── demo/
│   ├── run_demo.py            # 单问题 / 全部问题入口
│   ├── run_all.sh             # 一键跑全部三个杀手问题
│   └── questions.md           # 15 分钟讲解脚本
└── tests/
    ├── test_config.py
    ├── test_llm.py
    ├── test_seed_db.py
    ├── test_rag.py
    ├── test_nl2sql.py
    ├── test_graph_rag.py
    ├── test_agent.py
    ├── test_e2e.py
    └── test_mcp.py
```

## 快速开始

```bash
# 1. 安装依赖
cd agent-demo
pip install -r requirements.txt

# 2. 配置（演示用 mock 模式不需要 API Key）
cp .env.example .env

# 3. 初始化 SQLite
python -m data.seed_db

# 4. 跑全部三个杀手问题（mock 模式，60 秒内）
bash demo/run_all.sh

# 5. 单问题模式
python demo/run_demo.py --q "我们公司年假怎么算？"

# 6. 接真 LLM（DeepSeek 示例）
echo "LLM_MODE=real" >> .env
echo "LLM_BASE_URL=https://api.deepseek.com/v1" >> .env
echo "LLM_API_KEY=sk-your-key" >> .env
echo "LLM_MODEL=deepseek-chat" >> .env
bash demo/run_all.sh real
```

## 演示输出示例（mock 模式）

```
杀手问题 #1: 我们公司年假怎么算？试用期的员工呢？
[意图] search_docs
[工具] search_docs
  step1. search_docs(我们公司年假怎么算？...) → 员工年假按工作年限累计...
→ 回答：年假规则：工作满 1 年 5 天，满 5 年 10 天...

杀手问题 #2: 研发部上个月入职了多少人？分别是谁？
[意图] query_db
[工具] query_db
  step1. query_db(研发部上个月入职了多少人？...) → 共 1 条记录：郑十一
→ 回答：研发部上个月入职 1 人：郑十一

杀手问题 #3: 张三是研发部的吗？他适用什么制度？有什么资产？
[意图] graph_lookup
[工具] graph_lookup
  step1. graph_lookup(张三属于什么部门？) → 找到实体：员工:张三 → 部门:研发部...
→ 回答：[图谱路径：员工:张三 → 部门:研发部 → 制度:年假]
```

## 15 分钟面试讲解稿（按时间轴）

### [0:00-1:00] 开场 + 项目全景
- 自我介绍 + 一句话项目定位
- 打开 README「目录结构」段：7 个 JD 关键词 → 每个对应一个文件
- 强调「~2000 行代码、60 秒跑完三个杀手问题」

### [1:00-4:30] Q1 年假（RAG + Reflection，3.5 分钟）
- 跑：`LLM_MODE=mock python demo/run_demo.py --q "我们公司年假怎么算？试用期的员工呢？"`
- **边跑边讲**：
  - 打开 `src/agent.py`：Router → Planner → ReAct → Synthesizer
  - 打开 `src/rag.py`：LlamaIndex + ChromaDB + 本地 HF embedding
  - 演示 Reflection：从输出日志指出「第二次 search_docs 是反思后的二次检索」

### [4:30-7:00] Q2 研发部入职人数（NL2SQL，2.5 分钟）
- 跑：`python demo/run_demo.py --q "研发部上个月入职了多少人？分别是谁？"`
- **边跑边讲**：
  - 打开 `src/nl2sql.py`：schema 注入 + 安全白名单 + 反思重写
  - 打开 `prompts/nl2sql.jinja`：展示 few-shot 模板
  - 现场展示生成的 SQL（从打印日志里抓）

### [7:00-9:30] Q3 张三画像（Graph + DB 融合，2.5 分钟）
- 跑：`python demo/run_demo.py --q "张三是研发部的吗？他适用什么制度？有什么资产？"`
- **边跑边讲**：
  - 打开 `src/graph_rag.py`：NetworkX 跳查询逻辑
  - 打开 `data/graph.json`：离线预抽取的实体-关系图
  - 演示三工具协作：graph_lookup + query_db 查资产

### [9:30-12:00] MCP 工具调用（2.5 分钟）
- 打开 `src/mcp_server.py`，高亮三个 `@mcp.tool()` 装饰器
- 起 server（后台）：
  ```bash
  python -m src.mcp_server &
  ```
- 讲：MCP 让工具可被任何 Agent（Claude Desktop、未来 Coze 插件）调用

### [12:00-13:30] Prompt 工程与框架选型（1.5 分钟）
- 打开 `prompts/` 目录，逐个展示 5 个 jinja 模板
- 重点讲 `reflect.jinja`：让模型「承认不确定、主动换工具、不要瞎编」
- 讲为什么选 LangGraph 而不是 LangChain AgentExecutor：更细的状态控制、可调试、可观察

### [13:30-14:30] 测试 + 性能（1 分钟）
- 跑：`pytest tests/ -v`（29 个测试全绿）
- 讲三个性能考虑：本地 embedding（避免外网）、ReAct 步数上限（防死循环）、SQL 白名单（安全）

### [14:30-15:00] 收尾
- 「整套 ~2000 行代码、60 秒跑完三个杀手问题、覆盖 7 个 JD 关键词」
- 反问环节准备的问题：
  - 「你们业务里最看重的是 RAG 召回还是 NL2SQL 准确率？」
  - 「MCP 协议在公司内部系统里有没有在用？」

## JD 关键词 → 文件映射（面试官问任何点都能找到对应代码）

| JD 关键词 | 主文件 | 关键函数 / 类 |
|---|---|---|
| Graph RAG | `src/graph_rag.py` | `GraphRAG.lookup()` |
| NL2SQL | `src/nl2sql.py` | `NL2SQL.run()`, `sql_is_safe()` |
| ReAct / Reflection | `src/agent.py` | `react_loop_node()`, `reflect()` |
| MCP 工具调用 | `src/mcp_server.py` | `FastMCP("corp-knowledge-agent")` |
| LangGraph | `src/agent.py` | `build_graph()`, `AgentState` |
| LlamaIndex | `src/rag.py` | `DocSearcher.search()` |
| Prompt 工程 | `prompts/*.jinja` + `src/prompts.py` | 5 个模块化模板 |
| Python Web | (可选) `src/main.py` | argparse CLI |

## 离线 / 现场稳定性

- **mock 模式** (`LLM_MODE=mock`)：完全不依赖外部 API、跑通全部流程
- **本地 embedding**：sentence-transformers / paraphrase-multilingual-MiniLM-L12-v2
- **LLM 可切**：DeepSeek / OpenAI / MiniMax 都走 OpenAI 兼容协议
- **网络抖动回退**：mock 模式可兜底

## 测试覆盖

```
tests/
├── test_config.py     3 tests  # 配置加载
├── test_llm.py        3 tests  # LLM 单例 + mock
├── test_seed_db.py    4 tests  # SQLite 种子
├── test_rag.py        4 tests  # LlamaIndex 检索
├── test_nl2sql.py     7 tests  # NL2SQL + 安全白名单
├── test_graph_rag.py  5 tests  # NetworkX 跳查询
├── test_agent.py      8 tests  # LangGraph 状态机
├── test_e2e.py        5 tests  # 端到端 5 个种子问答
└── test_mcp.py        3 tests  # FastMCP 注册
                       ─────────
                       42 tests
```

## 后续扩展（YAGNI 清单，本期不做）

- 多用户会话管理
- 文档自动更新（CI 拉新文档重抽取图谱）
- Coze/Dify 平台对接
- 前端 UI（Gradio/Streamlit）
- 流式输出

## License

MIT