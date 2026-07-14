"""独立测试工具的 CLI：python -m src.tools_cli <tool> '<query>'"""
from __future__ import annotations

import json
import sys

from src.tools import TOOL_REGISTRY


def main():
    if len(sys.argv) < 3:
        print("用法: python -m src.tools_cli <tool> '<query>'")
        print(f"可用工具: {list(TOOL_REGISTRY.keys())}")
        sys.exit(1)
    tool_name = sys.argv[1]
    query = sys.argv[2]
    if tool_name not in TOOL_REGISTRY:
        print(f"未知工具: {tool_name}")
        sys.exit(1)
    result = TOOL_REGISTRY[tool_name](query)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()