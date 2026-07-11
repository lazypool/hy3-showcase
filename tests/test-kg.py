"""知识图谱创意应用的单元测试（无需 API Key）。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_extract_json():
    from kg import extract_json

    assert extract_json('{"a": 1}') == '{"a": 1}'
    assert extract_json("前文\n{\"a\": 1}\n后文") == '{"a": 1}'
    assert extract_json("no json") is None


def test_render_empty():
    from kg import render

    fig, ax = render({}, "test")
    assert fig is not None
    assert len(fig.axes) > 0


def test_render_with_data():
    from kg import render

    data = {
        "entities": [
            {"id": "1", "name": "A", "type": "concept"},
            {"id": "2", "name": "B", "type": "mechanism"},
        ],
        "relations": [{"source": "1", "target": "2", "label": "关联"}],
    }
    fig, ax = render(data, "test")
    assert fig is not None
