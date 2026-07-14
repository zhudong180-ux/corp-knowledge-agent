"""初始化 SQLite 数据库：departments / employees / assets + 种子数据。"""
from __future__ import annotations
import os, sqlite3
from datetime import date, timedelta

SCHEMA = """
CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, parent_id INTEGER REFERENCES departments(id));
CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept_id INTEGER NOT NULL REFERENCES departments(id), hire_date TEXT NOT NULL, level TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active');
CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id), type TEXT NOT NULL, model TEXT NOT NULL, issued_date TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'in_use');
CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(dept_id);
CREATE INDEX IF NOT EXISTS idx_asset_emp ON assets(employee_id);
"""

DEPARTMENTS = [(1,"研发部",None),(2,"产品部",None),(3,"市场部",None),(4,"HR部",None),(5,"行政部",None)]

def _d(days): return (date.today() - timedelta(days=days)).isoformat()

EMPLOYEES = [
    (1, "张三", 1, _d(730), "P5", "active"),
    (2, "李四", 1, _d(200), "P4", "active"),
    (3, "孙八", 1, _d(1500), "P6", "active"),
    (4, "周九", 1, _d(45), "P4", "active"),
    (5, "吴十", 1, _d(900), "P5", "active"),
    (6, "郑十一", 1, _d(30), "P4", "active"),
    (7, "王十二", 1, _d(400), "P5", "active"),
    (8, "冯十三", 1, _d(600), "P4", "active"),
    (9, "王五", 2, _d(1100), "P5", "active"),
    (10, "陈十四", 2, _d(300), "P4", "active"),
    (11, "褚十五", 2, _d(50), "P4", "active"),
    (12, "卫十六", 2, _d(800), "P5", "active"),
    (13, "蒋十七", 2, _d(500), "P3", "active"),
    (14, "赵六", 3, _d(950), "P4", "active"),
    (15, "沈十八", 3, _d(120), "P4", "active"),
    (16, "韩十九", 3, _d(350), "P3", "active"),
    (17, "钱七", 4, _d(1400), "P5", "active"),
    (18, "杨二十", 4, _d(250), "P4", "active"),
    (19, "朱二一", 4, _d(40), "P3", "active"),
    (20, "秦二二", 4, _d(700), "P4", "active"),
    (21, "尤二三", 5, _d(1300), "P4", "active"),
    (22, "许二四", 5, _d(450), "P3", "active"),
    (23, "何二五", 5, _d(180), "P3", "active"),
    (24, "吕二六", 5, _d(85), "P3", "active"),
    (25, "施二七", 5, _d(1000), "P4", "active"),
    (26, "张二八", 5, _d(550), "P3", "active"),
    (27, "孔二九", 5, _d(220), "P3", "active"),
    (28, "曹三十", 1, _d(750), "P5", "active"),
    (29, "严三一", 2, _d(380), "P4", "active"),
    (30, "华三二", 3, _d(620), "P4", "active"),
]

ASSETS = [
    (1, 1, "笔记本", "MacBook Pro 14 M3 Pro", _d(730), "in_use"),
    (2, 3, "笔记本", "MacBook Pro 16 M3 Max", _d(1500), "in_use"),
    (3, 2, "笔记本", "ThinkPad X1 Carbon", _d(200), "in_use"),
    (4, 1, "显示器", "Dell U2723QE", _d(600), "in_use"),
    (5, 9, "笔记本", "MacBook Pro 14 M3 Pro", _d(1100), "in_use"),
    (6, 9, "显示器", "Dell U2723QE", _d(1100), "in_use"),
    (7, 14, "笔记本", "ThinkPad X1 Carbon", _d(950), "in_use"),
    (8, 17, "笔记本", "MacBook Pro 14 M3 Pro", _d(1400), "in_use"),
    (9, 5, "笔记本", "MacBook Pro 14 M3 Pro", _d(900), "in_use"),
    (10, 5, "显示器", "Dell U2723QE", _d(900), "in_use"),
    (11, 7, "笔记本", "MacBook Pro 14 M3 Pro", _d(400), "in_use"),
    (12, 7, "显示器", "Dell U2723QE", _d(400), "in_use"),
    (13, 12, "笔记本", "MacBook Pro 14 M3 Pro", _d(800), "in_use"),
    (14, 28, "笔记本", "MacBook Pro 14 M3 Pro", _d(750), "in_use"),
    (15, 28, "显示器", "Dell U2723QE", _d(750), "in_use"),
    (16, 11, "笔记本", "MacBook Pro 14 M3 Pro", _d(50), "in_use"),
    (17, 6, "笔记本", "MacBook Pro 14 M3 Pro", _d(30), "in_use"),
    (18, 4, "笔记本", "MacBook Pro 14 M3 Pro", _d(45), "in_use"),
    (19, 19, "笔记本", "ThinkPad X1 Carbon", _d(40), "in_use"),
    (20, 18, "笔记本", "ThinkPad X1 Carbon", _d(250), "in_use"),
]

def build_seed_db(db_path):
    if os.path.exists(db_path): os.remove(db_path)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO departments (id, name, parent_id) VALUES (?, ?, ?)", DEPARTMENTS)
        conn.executemany("INSERT INTO employees (id, name, dept_id, hire_date, level, status) VALUES (?, ?, ?, ?, ?, ?)", EMPLOYEES)
        conn.executemany("INSERT INTO assets (id, employee_id, type, model, issued_date, status) VALUES (?, ?, ?, ?, ?, ?)", ASSETS)
        conn.commit()
    finally: conn.close()

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "./data/employees.db"
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    build_seed_db(target)
    print(f"Seeded SQLite DB at {target}")