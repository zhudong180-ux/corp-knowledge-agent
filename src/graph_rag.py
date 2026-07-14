"""NetworkX 知识图谱查询：实体定位 + 1~2 跳关系扩展。"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

import networkx as nx

from src.config import get_settings


def _extract_entity(question: str) -> Optional[str]:
    """从问题里提取第一个员工/部门/制度名作为锚点实体。"""
    patterns = [
        r"员工[:：](\S+)",
        r"部门[:：](\S+)",
        r"制度[:：](\S+)",
        r"资产[:：](\S+)",
    ]
    for p in patterns:
        m = re.search(p, question)
        if m:
            return m.group(1)
    # 优先匹配「X属于/适用/在/是」前的姓名（2-3 字）
    m = re.search(r"([\u4e00-\u9fa5]{2,3})(属于|适用|在|是|的|有|隶属)", question)
    if m:
        return m.group(1)
    # 兜底：取第一个 2-3 字中文片段
    m = re.search(r"[\u4e00-\u9fa5]{2,3}", question)
    if m:
        return m.group(0)
    return None


class GraphRAG:
    """加载 graph.json，构建 NetworkX 图，支持实体查询 + N 跳扩展。"""

    def __init__(self, graph_path: Optional[str] = None):
        s = get_settings()
        path = graph_path or s.graph_path
        self.graph = nx.DiGraph()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for n in data.get("nodes", []):
            attrs = {"type": n.get("type"), **n.get("attrs", {})}
            self.graph.add_node(n["id"], **attrs)
        for e in data.get("edges", []):
            self.graph.add_edge(e["src"], e["dst"], rel=e["rel"])

    def lookup(self, question: str, max_hops: int = 2) -> dict:
        entity = _extract_entity(question)
        if not entity:
            return {"entity": None, "answer": "未找到问题中的实体。", "path": []}

        # 模糊匹配：节点 id 包含实体名
        candidates = [n for n in self.graph.nodes if entity in n]
        if not candidates:
            return {"entity": entity, "answer": f"未找到实体 '{entity}'。", "path": []}

        # 用第一个候选做 N 跳扩展
        anchor = candidates[0]
        reachable = []
        for target in self.graph.nodes:
            if target == anchor:
                continue
            try:
                path = nx.shortest_path(self.graph, anchor, target)
                if 1 <= len(path) - 1 <= max_hops:
                    edges = []
                    for i in range(len(path) - 1):
                        edges.append(self.graph.edges[path[i], path[i + 1]]["rel"])
                    reachable.append({
                        "path": path,
                        "edges": edges,
                        "length": len(path) - 1,
                    })
            except nx.NetworkXNoPath:
                continue

        reachable.sort(key=lambda x: x["length"])
        if not reachable:
            return {"entity": anchor, "answer": f"找到 {anchor}，但无关联节点。", "path": []}

        bits = [f"找到实体：{anchor}。"]
        for r in reachable[:5]:
            path_str = " -> ".join(
                f"[{r['edges'][i]}] {r['path'][i+1]}" for i in range(len(r["path"]) - 1)
            )
            bits.append(f"  · {r['path'][0]} → {r['path'][-1]}（{r['length']} 跳：{path_str}）")
        return {"entity": anchor, "answer": "\n".join(bits), "path": reachable[:5]}