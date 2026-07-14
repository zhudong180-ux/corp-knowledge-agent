# 15 分钟面试讲解脚本

按时间段标注的演示节奏。每一段都有「做什么」「说什么」「打开哪个文件」。

---

## [0:00-1:00] 开场 + 项目全景

**做什么：**
- 自我介绍（30 秒）
- 打开 README.md 滚到「15 分钟面试讲解稿」段
- 强调：「7 个 JD 关键词 → 7 个文件映射，60 秒跑完三个杀手问题」

**说什么：**
"这个项目做的是一个企业知识库智能体，对应到我们岗位 JD 上，
能覆盖 7 个核心关键词。我会用三个杀手问题演示完整闭环。"

**打开文件：** `README.md`

---

## [1:00-4:30] Q1：年假（RAG + Reflection）

**做什么：**
- 在终端跑：
  ```bash
  cd agent-demo
  LLM_MODE=mock python demo/run_demo.py --q "我们公司年假怎么算？试用期的员工呢？"
  ```
- 边跑边切窗口讲代码

**说什么：**
"看，第一次 search_docs 没找到「试用期」相关内容，
触发了 Reflection，又跑了一次 graph_lookup 来补全。
这就是 ReAct + Reflection 的标准 pattern。"

**打开文件（按顺序）：**
1. `src/agent.py` 的 `react_loop_node()` 函数
2. `src/rag.py` 的 `DocSearcher.search()`
3. `prompts/reflect.jinja`

---

## [4:30-7:00] Q2：研发部入职人数（NL2SQL）

**做什么：**
- 跑：
  ```bash
  python demo/run_demo.py --q "研发部上个月入职了多少人？分别是谁？"
  ```

**说什么：**
"看它生成的 SQL：先 JOIN departments，再按 hire_date 过滤。
我们的 prompt 里写明了 few-shot，模型能直接套 schema 模板。"

**打开文件：**
1. `src/nl2sql.py` 的 `NL2SQL.generate_sql()` 和 `sql_is_safe()`
2. `prompts/nl2sql.jinja`（讲 few-shot 模板）

---

## [7:00-9:30] Q3：张三画像（Graph + DB 融合）

**做什么：**
- 跑：
  ```bash
  python demo/run_demo.py --q "张三是研发部的吗？他适用什么制度？有什么资产？"
  ```

**说什么：**
"这个问题同时调了 graph_lookup（查关系）和 query_db（查资产）。
最终答案把两个工具的结果融合在一起——
这就是 Graph RAG + 结构化数据的混合架构。"

**打开文件：**
1. `src/graph_rag.py` 的 `GraphRAG.lookup()`
2. `data/graph.json`（离线预抽取的图谱）
3. `src/agent.py` 的 `synthesizer_node()`（讲融合逻辑）

---

## [9:30-12:00] MCP 工具调用

**做什么：**
- 打开 `src/mcp_server.py`，高亮三个 `@mcp.tool()` 装饰器
- 起 server（后台）：
  ```bash
  python -m src.mcp_server &
  ```
- 讲：MCP 让工具可被任何 Agent（Claude Desktop、未来 Coze 插件）调用

**说什么：**
"我们用 FastMCP 把这三个工具暴露成 MCP 标准协议。
实际生产里，Coze / Dify / Claude Desktop 都能直接调用我的工具，
不需要重写。这是 JD 里 MCP 工具调用的硬性交付。"

---

## [12:00-13:30] Prompt 工程与框架选型

**做什么：**
- 打开 `prompts/` 目录，逐个展示 5 个 jinja 模板
- 重点讲 `reflect.jinja`：

**说什么：**
"Prompt 工程里我特别重视 reflect 这个模板。
它告诉模型：'如果工具结果不够，主动承认不确定、换工具或换关键词，不要瞎编。'
这是大模型应用里最容易被忽视但最关键的部分。"

**打开文件：** `prompts/reflect.jinja`、`src/agent.py` 的 `reflect()` 函数

---

## [13:30-14:30] 测试 + 性能

**做什么：**
- 跑：
  ```bash
  pytest tests/ -v
  ```
- 数一下 PASS 的测试数（约 42 个）

**说什么：**
"性能上有三个考虑：
1. 本地 embedding，避免外网依赖；
2. ReAct 步数上限 3 步，防止死循环；
3. SQL 白名单只允许 SELECT，保证安全。"

---

## [14:30-15:00] 收尾

**说什么：**
"整套项目 ~2000 行代码，60 秒跑完三个杀手问题，
覆盖 7 个 JD 关键词。代码、Prompt、测试都齐了，
直接 `git clone && bash demo/run_all.sh` 就能跑。"

**反问准备：**
- 「你们业务里最看重 RAG 召回率还是 NL2SQL 准确率？」
- 「MCP 协议在公司内部系统里有规划吗？」
- 「你们的 Agent 是单 Agent 还是多 Agent 协作？」

---

## 紧急情况应对

| 情况 | 应对 |
|---|---|
| LLM API 超时 | `LLM_MODE=mock` 一键切离线模式 |
| Embedding 模型下载慢 | 提前下载到 `.embed_cache/` |
| 测试 fail | 跑 `pytest tests/ -v` 看哪个红了，跳过讲代码 |
| 网络完全断 | mock 模式可完整演示，**不需要网络** |