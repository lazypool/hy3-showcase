import os, sys

if not os.environ.get("HY3_API_KEY"):
    raise RuntimeError("需要设置 HY3_API_KEY 环境变量才能运行 e2e 测试")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hy3_showcase import Hy3Client


def setup():
    os.environ.pop("HY3_MOCK", None)
    return Hy3Client()


def test_chat():
    c = setup()
    r = c.chat([{"role":"user","content":"你好"}], stream=False)
    assert r["content"]

def test_stream():
    c = setup()
    chunks = list(c.chat([{"role":"user","content":"写一个快排"}], stream=True))
    assert chunks

def test_reasoning():
    c = setup()
    r = c.chat([{"role":"user","content":"24点：3,3,8,8"}],
               stream=False, reasoning_effort="high")
    assert "24" in r["content"]

def test_tool_call():
    c = setup()
    tools = [{"type":"function","function":{"name":"calc","description":"计算器",
        "parameters":{"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]}}}]
    r = c.chat_with_tools([{"role":"user","content":"计算 1+1"}], tools=tools)
    assert r.get("content") or r.get("tool_calls")


import json


def test_kg_extraction():
    c = setup()
    content = ""
    for chunk in c.chat(
        [
            {"role": "system", "content": "提取关于「Transformer」的核心概念和关系，以 JSON 格式输出"},
            {"role": "user", "content": "分析 Transformer"},
        ],
        stream=True,
        reasoning_effort="high",
    ):
        content += chunk["content"]

    data = json.loads(content)
    concepts = data.get("entities") or data.get("core_concepts") or []
    assert len(concepts) >= 4
    raw = json.dumps(data)
    assert "Transformer" in raw or "transformer" in raw.lower()


def test_kg_explanation():
    c = setup()
    explain = ""
    for chunk in c.chat(
        [
            {"role": "system", "content": "用通俗的语言解释 Transformer 的核心概念"},
            {"role": "user", "content": "解释 Transformer"},
        ],
        stream=True,
        reasoning_effort="low",
    ):
        explain += chunk["content"]

    assert "Transformer" in explain
