"""NL2SQL：自然语言 → SQL（LLM 生成或 mock 规则）→ 安全检查 → 执行。"""
from __future__ import annotations

import re
import sqlite3
from typing import Optional

from src.config import get_settings
from src.llm import get_llm


SCHEMA_DESC = """
表结构：
- departments(id, name, parent_id)
- employees(id, name, dept_id, hire_date, level, status)
- assets(id, employee_id, type, model, issued_date, status)

注意：
- 日期是 TEXT 类型，格式 YYYY-MM-DD
- 当前日期可通过 date('now') 获取
- 「上个月」可用 date('now', 'start of month', '-1 month') 到 date('now', 'start of month')
- 部门名在 departments 表，关联用 dept_id
"""


FORBIDDEN = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|CREATE|REPLACE)\b", re.IGNORECASE)


def sql_is_safe(sql: str) -> bool:
    """白名单校验：必须以 SELECT 开头，且不含写操作关键字。"""
    sql = sql.strip().rstrip(";")
    if not re.match(r"^\s*SELECT", sql, re.IGNORECASE):
        return False
    if FORBIDDEN.search(sql):
        return False
    return True


def _mock_sql(question: str) -> str:
    q = question
    if "研发部" in q and ("入职" in q or "上个月" in q):
        return (
            "SELECT e.name, e.hire_date FROM employees e "
            "JOIN departments d ON e.dept_id = d.id "
            "WHERE d.name = '研发部' "
            "AND e.hire_date >= date('now', 'start of month', '-1 month') "
            "AND e.hire_date < date('now', 'start of month');"
        )
    if "张三" in q and ("资产" in q or "笔记本" in q):
        return (
            "SELECT a.type, a.model, a.issued_date FROM assets a "
            "JOIN employees e ON a.employee_id = e.id "
            "WHERE e.name = '张三';"
        )
    if "员工" in q and "研发部" in q:
        return "SELECT e.name FROM employees e JOIN departments d ON e.dept_id=d.id WHERE d.name='研发部';"
    if "资产" in q and "张三" in q:
        return "SELECT a.type, a.model FROM assets a JOIN employees e ON a.employee_id=e.id WHERE e.name='张三';"
    if "入职" in q and "多少人" in q:
        return (
            "SELECT COUNT(*) AS total FROM employees "
            "WHERE hire_date >= date('now', 'start of month', '-1 month') "
            "AND hire_date < date('now', 'start of month');"
        )
    return "SELECT COUNT(*) AS total FROM employees;"


class NL2SQL:
    """自然语言 → SQL → 执行结果。"""

    def __init__(self, db_path: Optional[str] = None, mode: Optional[str] = None):
        s = get_settings()
        self.db_path = db_path or s.sqlite_path
        self.mode = mode or s.llm_mode
        self.llm = get_llm()

    def generate_sql(self, question: str) -> str:
        if self.mode == "mock":
            return _mock_sql(question)
        prompt = (
            "你是 SQL 生成助手。根据 schema 把问题转成 SELECT SQL。\n"
            f"{SCHEMA_DESC}\n问题：{question}\n只输出 SQL，不要解释："
        )
        resp = self.llm.invoke(prompt)
        sql = resp.content.strip()
        # 去掉 <think>...</think> 推理块（MiniMax-M2 等推理模型会输出）
        sql = re.sub(r"<think>.*?</think>", "", sql, flags=re.DOTALL | re.IGNORECASE)
        # 去掉 markdown 代码块包裹（```sql / ```SQL / 裸 ``` 都处理）
        sql = re.sub(r"^```(?:sql|SQL)?\s*", "", sql, flags=re.MULTILINE)
        sql = re.sub(r"\s*```\s*$", "", sql, flags=re.MULTILINE)
        return sql.strip()

    def run(self, question: str) -> dict:
        sql = self.generate_sql(question)
        safe = sql_is_safe(sql)
        if not safe:
            return {"sql": sql, "rows": [], "columns": [], "answer": "SQL 未通过安全校验。", "error": "unsafe_sql"}
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(sql)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
        except Exception as e:
            return {"sql": sql, "rows": [], "columns": [], "answer": f"查询失败：{e}", "error": str(e)}
        finally:
            conn.close()
        rows_dict = [dict(zip(cols, r)) for r in rows]
        answer = self._format_answer(question, rows_dict)
        return {"sql": sql, "rows": rows_dict, "columns": cols, "answer": answer}

    def _format_answer(self, question: str, rows: list[dict]) -> str:
        if not rows:
            return "未查询到数据。"
        if "研发部" in question and len(rows) <= 10 and "name" in rows[0]:
            names = "、".join(r.get("name", "?") for r in rows)
            return f"共 {len(rows)} 条记录：{names}"
        if rows and "total" in rows[0]:
            return f"总计 {rows[0]['total']} 条。"
        if rows and "name" in rows[0] and "hire_date" in rows[0]:
            names = "、".join(r.get("name", "?") for r in rows)
            return f"入职名单：{names}"
        return f"查询到 {len(rows)} 条记录。"