import json

import pytest

from src.graph_rag import GraphRAG, _extract_entity


@pytest.fixture
def sample_graph():
    return {
        "nodes": [
            {"id": "员工:张三", "type": "Employee"},
            {"id": "部门:研发部", "type": "Department"},
            {"id": "制度:年假", "type": "Policy"},
        ],
        "edges": [
            {"src": "员工:张三", "rel": "BELONGS_TO", "dst": "部门:研发部"},
            {"src": "部门:研发部", "rel": "SUBJECT_TO", "dst": "制度:年假"},
        ],
    }


@pytest.fixture
def engine(tmp_path, sample_graph):
    p = tmp_path / "g.json"
    p.write_text(json.dumps(sample_graph), encoding="utf-8")
    return GraphRAG(str(p))


def test_extract_entity_chinese_name():
    assert _extract_entity("张三属于什么部门") == "张三"


def test_extract_entity_with_prefix():
    assert _extract_entity("员工:李四 适用什么制度") == "李四"


def test_lookup_department_of_employee(engine):
    r = engine.lookup("张三属于什么部门")
    assert "研发部" in r["answer"]
    assert r["entity"] == "员工:张三"


def test_lookup_2hop(engine):
    r = engine.lookup("张三 适用什么制度")
    assert "年假" in r["answer"]
    assert any(p["length"] == 2 for p in r["path"])


def test_lookup_unknown_entity(engine):
    r = engine.lookup("不存在的某某")
    assert "未找到" in r["answer"] or r["entity"] is None