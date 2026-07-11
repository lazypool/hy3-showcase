import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hy3_showcase import Hy3Client


def setup():
    os.environ["HY3_MOCK"] = "true"
    return Hy3Client()


def test_chat():
    c = setup()
    r = c.chat([{"role": "user", "content": "你好"}], stream=False)
    assert r["content"]
    assert "Hy3" in r["content"]

def test_stream():
    c = setup()
    chunks = list(c.chat([{"role": "user", "content": "介绍自己"}], stream=True))
    assert len(chunks) >= 2
    assert "".join(c["content"] for c in chunks)

def test_quicksort():
    c = setup()
    r = c.chat([{"role": "user", "content": "用 Python 写一个快速排序"}], stream=False)
    assert "quicksort" in r["content"].lower()

def test_moe():
    c = setup()
    r = c.chat([{"role": "user", "content": "解释 MoE 架构"}], stream=False)
    assert "MoE" in r["content"]

def test_reasoning():
    c = setup()
    r = c.chat([{"role": "user", "content": "24点：3,3,8,8"}],
               stream=False, reasoning_effort="high")
    assert "24" in r["content"]

def test_tool_call():
    c = setup()
    tools = [{"type":"function","function":{"name":"calculator","description":"计算器",
        "parameters":{"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]}}}]
    r = c.chat_with_tools(
        [{"role":"user","content":"计算 (238491 * 78345) / 100"}], tools=tools)
    assert r.get("tool_calls")
    assert "calculator" in r["tool_calls"][0]["function"]["name"]

def test_distributed():
    c = setup()
    r = c.chat([{"role":"user","content":"设计分布式缓存"}], stream=False)
    assert "分布式" in r["content"]

def test_flask():
    c = setup()
    r = c.chat([{"role":"user","content":"Flask 待办应用"}], stream=False)
    assert "Flask" in r["content"]
