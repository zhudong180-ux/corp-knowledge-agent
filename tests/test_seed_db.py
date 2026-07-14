import os
import sqlite3
import tempfile

from data.seed_db import build_seed_db


def test_build_seed_db_creates_three_tables():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        build_seed_db(db_path)
        conn = sqlite3.connect(db_path)
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        conn.close()
        assert {"departments", "employees", "assets"}.issubset(tables)


def test_employees_count_at_least_20():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        build_seed_db(db_path)
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        conn.close()
        assert count >= 20


def test_assets_count_at_least_15():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        build_seed_db(db_path)
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        conn.close()
        assert count >= 15


def test_employees_have_recent_hires():
    """至少 1 个员工入职日期在最近 60 天内。"""
    with tempfile.TemporaryDirectory() as tmp:
        db_path = os.path.join(tmp, "test.db")
        build_seed_db(db_path)
        conn = sqlite3.connect(db_path)
        cur = conn.execute(
            "SELECT COUNT(*) FROM employees WHERE hire_date >= date('now', '-60 days')"
        )
        count = cur.fetchone()[0]
        conn.close()
        assert count >= 1