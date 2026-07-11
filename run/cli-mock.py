#!/usr/bin/env python3
"""CLI + Mock 模式演示。"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["HY3_MOCK"] = "true"

os.makedirs(os.path.join(ROOT, "demo"), exist_ok=True)
log = open(os.path.join(ROOT, "demo", "cli-mock.txt"), "w")

def _print(*args, **kwargs):
    kwargs.setdefault("file", sys.stdout)
    print(*args, **kwargs)
    kwargs["file"] = log
    print(*args, **kwargs)

def _check(name, ok_flag):
    global ok, fail
    if ok_flag:
        ok += 1
        _print(f"  ✓ PASS  {name}")
    else:
        fail += 1
        _print(f"  ✗ FAIL  {name}")

from hy3_showcase import Hy3Client

c = Hy3Client()
ok = fail = 0

_print("=== Hy3 CLI + Mock ===")

_print("\n--- 1. 基础对话 ---")
r = c.chat([{"role": "user", "content": "你好"}], stream=False)
_print(f"  > 你好\n  < {r['content']}")
_check("非流式返回", bool(r["content"]))
_check("含 Hy3 自我介绍", "Hy3" in r["content"])

_print("\n--- 2. MoE 架构 ---")
r = c.chat([{"role": "user", "content": "解释 MoE 架构"}], stream=False)
_print(f"  > 解释 MoE 架构\n  < {r['content']}")
_check("MoE 关键词", "MoE" in r["content"])

_print("\n--- 3. 快速排序 ---")
r = c.chat([{"role": "user", "content": "用 Python 写快排"}], stream=False)
_print(f"  > 用 Python 写快排")
_check("含 quicksort", "quicksort" in r["content"].lower())

_print("\n--- 4. 流式输出 ---")
chunks = list(c.chat([{"role": "user", "content": "介绍自己"}], stream=True))
text = "".join(c["content"] for c in chunks)
_print(f"  > 介绍自己\n  < {len(chunks)} chunks, {len(text)} 字")
_check(">= 2 chunks", len(chunks) >= 2)

_print("\n--- 5. 深度推理 ---")
r = c.chat(
    [{"role": "user", "content": "24点：3,3,8,8"}],
    stream=False,
    reasoning_effort="high",
)
_print(f"  > 24点：3,3,8,8\n  < {r['content']}")
_check("含 24", "24" in r["content"])

_print("\n--- 6. 工具调用 ---")
tools = [{"type":"function","function":{"name":"calculator","description":"计算器",
    "parameters":{"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]}}}]
r = c.chat_with_tools(
    [{"role": "user", "content": "计算 (238491*78345)/100"}], tools=tools
)
_print(f"  > 计算 (238491*78345)/100")
if r.get("tool_calls"):
    _print(f"  < 调用 {r['tool_calls'][0]['function']['name']}")
_check("有工具调用", bool(r.get("tool_calls")))

_print(f"\n=== 结果: {ok}/{ok+fail} 通过, {fail} 失败 ===")
log.close()
sys.exit(0 if fail == 0 else 1)
