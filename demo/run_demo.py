"""单问题演示脚本：python demo/run_demo.py --q '年假怎么算？'

也可一键跑全部三个杀手问题：python demo/run_demo.py --all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 允许从项目根目录跑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import run_agent


KILLER_QUESTIONS = [
    "我们公司年假怎么算？试用期的员工呢？",
    "研发部上个月入职了多少人？分别是谁？",
    "张三是研发部的吗？他适用什么制度？有什么资产？",
]


def _print_step(idx: int, s: dict) -> None:
    res = s["result"]
    brief = res.get("answer") or json.dumps(res, ensure_ascii=False, default=str)[:120]
    print(f"  step{idx}. {s['tool']}({s['sub_query'][:40]}) → {brief[:100]}")


def main():
    parser = argparse.ArgumentParser(description="corp-knowledge-agent demo runner")
    parser.add_argument("--q", type=str, help="单问题模式")
    parser.add_argument("--all", action="store_true", help="跑全部三个杀手问题")
    parser.add_argument("--verbose", action="store_true", default=True)
    args = parser.parse_args()

    if args.all:
        for i, q in enumerate(KILLER_QUESTIONS, 1):
            print(f"\n{'='*60}\n杀手问题 #{i}: {q}\n{'='*60}")
            r = run_agent(q)
            print(f"\n[意图] {r['intent']}")
            print(f"[工具] {', '.join(r['tools_used'])}")
            if args.verbose:
                for j, s in enumerate(r["steps"], 1):
                    _print_step(j, s)
            print(f"\n→ 回答：{r['answer']}\n")
        return

    if not args.q:
        parser.print_help()
        return

    r = run_agent(args.q)
    print(f"[意图] {r['intent']}")
    print(f"[工具] {', '.join(r['tools_used'])}")
    if args.verbose:
        for j, s in enumerate(r["steps"], 1):
            _print_step(j, s)
    print(f"\n→ {r['answer']}")


if __name__ == "__main__":
    main()