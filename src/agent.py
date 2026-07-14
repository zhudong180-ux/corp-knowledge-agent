"""LangGraph ReAct Agent：Router → Planner → ReAct Loop → Synthesizer。

支持规则路由（关键词匹配）+ LLM 兜底分类；ReAct 循环最多 N 步；Reflection 触发重试。
"""
from __future__ import annotations

import json
import re
from typing import TypedDict

from src.config import get_settings
from src.llm import get_llm
from src.prompts import render
from src.tools import TOOL_REGISTRY


# ============ 规则路由 ============
# 顺序：先匹配具体的查询意图（含"多少/属于"优先于"资产"）。
_RULE_PATTERNS = [
    (re.compile(r"多少|几个|名单"), "query_db"),
    (re.compile(r"属于|隶属于|适用|关系|哪些部门"), "graph_lookup"),
    (re.compile(r"申请.*流程|怎么申请|如何申请|政策|怎么算|规定|报销|配发|制度"), "search_docs"),
    (re.compile(r"资产|笔记本|名下"), "query_db"),
]


def route_by_rule(question: str) -> str | None:
    for pat, tool in _RULE_PATTERNS:
        if pat.search(question):
            return tool
    return None


def route_by_llm(question: str) -> str:
    llm = get_llm()
    out = llm.invoke(render("router", question=question)).content.strip().lower()
    for tool in TOOL_REGISTRY:
        if tool in out:
            return tool
    return "search_docs"  # fallback


# ============ Planner ============
def plan(question: str, primary_tool: str) -> list[dict]:
    """根据主工具拆分子任务。规则模式下拆 1 步；LLM 模式下拆多步。"""
    if get_settings().llm_mode == "mock" or primary_tool != "search_docs":
        return [{"tool": primary_tool, "sub_query": question}]
    try:
        llm = get_llm()
        out = llm.invoke(render("planner", question=question)).content.strip()
        out = re.sub(r"^```json\s*|^```\s*|\s*```$", "", out, flags=re.MULTILINE).strip()
        plan_list = json.loads(out)
        if isinstance(plan_list, list):
            return plan_list
    except Exception:
        pass
    return [{"tool": primary_tool, "sub_query": question}]


# ============ Reflection ============
def reflect(question: str, tool_name: str, tool_result: dict) -> tuple[bool, str]:
    """返回 (是否够用, 重试建议)。"""
    if tool_result.get("error"):
        return False, f"工具 {tool_name} 出错：{tool_result['error']}，建议换工具。"
    if not tool_result.get("chunks") and not tool_result.get("rows") and not tool_result.get("path"):
        return False, f"工具 {tool_name} 返回空，建议换关键词或换工具。"

    try:
        llm = get_llm()
        result_str = json.dumps(tool_result, ensure_ascii=False, default=str)[:500]
        prompt = render("reflect", question=question, tool_name=tool_name, tool_result=result_str)
        out = llm.invoke(prompt).content.strip()
        if out.upper().startswith("OK"):
            return True, ""
        if "RETRY" in out.upper():
            suggestion = out.split(":", 1)[1].strip() if ":" in out else "换工具或换关键词"
            return False, suggestion
    except Exception:
        pass
    return True, ""


# ============ LangGraph State ============
class AgentState(TypedDict, total=False):
    question: str
    intent: str
    plan: list
    steps: list
    reflection_count: int
    final_answer: str
    sources: list


# ============ Node implementations ============
def router_node(state: AgentState) -> AgentState:
    q = state["question"]
    intent = route_by_rule(q) or route_by_llm(q)
    state["intent"] = intent
    state["steps"] = []
    state["reflection_count"] = 0
    return state


def planner_node(state: AgentState) -> AgentState:
    state["plan"] = plan(state["question"], state["intent"])
    return state


def react_loop_node(state: AgentState) -> AgentState:
    s = get_settings()
    max_steps = s.max_react_steps
    max_refl = s.max_reflections

    for i, sub in enumerate(state["plan"]):
        if i >= max_steps:
            break
        tool = sub["tool"]
        sub_q = sub["sub_query"]
        if tool not in TOOL_REGISTRY:
            state["steps"].append({"tool": tool, "sub_query": sub_q, "result": {"error": "unknown tool"}})
            continue

        result = TOOL_REGISTRY[tool](sub_q)
        state["steps"].append({"tool": tool, "sub_query": sub_q, "result": result})

        # Reflection: 失败则换一个工具重试
        if state["reflection_count"] < max_refl:
            ok, suggestion = reflect(state["question"], tool, result)
            if not ok and state["reflection_count"] < max_refl:
                state["reflection_count"] += 1
                alt_tool = "graph_lookup" if tool != "graph_lookup" else "search_docs"
                if alt_tool in TOOL_REGISTRY:
                    alt_result = TOOL_REGISTRY[alt_tool](state["question"])
                    state["steps"].append({
                        "tool": alt_tool,
                        "sub_query": f"[reflection] {state['question']}",
                        "result": alt_result,
                    })

    return state


def synthesizer_node(state: AgentState) -> AgentState:
    llm = get_llm()
    steps_brief = []
    sources = []
    for s in state["steps"]:
        r = s["result"]
        if "chunks" in r:
            brief = "\n".join(c["text"][:200] for c in r["chunks"][:2])
            sources.extend(c.get("source", "?") for c in r["chunks"][:2])
        elif "answer" in r:
            brief = r["answer"][:300]
        else:
            brief = json.dumps(r, ensure_ascii=False, default=str)[:300]
        steps_brief.append({"tool": s["tool"], "sub_query": s["sub_query"], "result": brief})

    try:
        prompt = render("synthesize", question=state["question"], steps=steps_brief)
        out = llm.invoke(prompt).content.strip()
    except Exception:
        for s in state["steps"]:
            if "answer" in s["result"]:
                out = s["result"]["answer"]
                break
        else:
            out = "抱歉，我暂时无法回答这个问题，建议联系 HR 或 IT。"

    state["final_answer"] = out
    state["sources"] = list(set(sources))
    return state


# ============ LangGraph Wiring ============
def build_graph():
    """构造 LangGraph 状态机。"""
    from langgraph.graph import END, StateGraph

    g = StateGraph(AgentState)
    g.add_node("router", router_node)
    g.add_node("planner", planner_node)
    g.add_node("react", react_loop_node)
    g.add_node("synthesizer", synthesizer_node)

    g.set_entry_point("router")
    g.add_edge("router", "planner")
    g.add_edge("planner", "react")
    g.add_edge("react", "synthesizer")
    g.add_edge("synthesizer", END)
    return g.compile()


def run_agent(question: str) -> dict:
    """主入口：跑一次完整智能体。"""
    graph = build_graph()
    final = graph.invoke({"question": question})
    return {
        "question": question,
        "intent": final.get("intent"),
        "steps": final.get("steps", []),
        "tools_used": list({s["tool"] for s in final.get("steps", [])}),
        "answer": final.get("final_answer", ""),
        "sources": final.get("sources", []),
    }