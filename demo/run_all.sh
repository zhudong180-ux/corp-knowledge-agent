#!/usr/bin/env bash
# 一键跑完三个杀手问题，用于面试现场演示。
# 用法：bash demo/run_all.sh [mock|real]
set -e

cd "$(dirname "$0")/.."

MODE="${1:-mock}"
export LLM_MODE="$MODE"

echo "==============================="
echo " corp-knowledge-agent 全流程演示"
echo " 模式: $MODE"
echo "==============================="

# 1. 确保 SQLite 存在
if [ ! -f data/employees.db ]; then
  echo "→ 初始化 SQLite..."
  python -m data.seed_db
fi

# 2. 跑三个杀手问题
LLM_MODE="$MODE" python demo/run_demo.py --all