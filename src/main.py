"""CLI 入口：单问题交互，走完整 LangGraph agent。"""
from __future__ import annotations

import argparse
import json

from src.agent import run_agent


def main():
    parser = argparse.ArgumentParser(description="corp-knowledge-agent CLI")
    parser.add_argument("--q", "--question", type=str, help="单次提问后退出")
    parser.add_argument("--verbose", action="store_true", help="打印工具调用日志")
    args = parser.parse_args()

    if not args.q:
        print("corp-knowledge-agent v0.5")
        print("用法: python -m src.main --q '你的问题' [--verbose]")
        return

    result = run_agent(args.q)
    if args.verbose:
        print(f"\n[意图] {result['intent']}")
        print(f"[工具] {', '.join(result['tools_used'])}")
        for i, s in enumerate(result["steps"], 1):
            r = s["result"]
            brief = r.get("answer") or str(r)[:100]
            print(f"  step{i}.{s['tool']}({s['sub_query'][:30]}) -> {brief[:80]}")
        print()
    print(result["answer"])


if __name__ == "__main__":
    main()