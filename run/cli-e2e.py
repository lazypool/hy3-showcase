#!/usr/bin/env python3
"""CLI + 真实 API 演示。需要 HY3_API_KEY 环境变量。"""
import os, sys

if not os.environ.get("HY3_API_KEY"):
    print("❌ 需要设置 HY3_API_KEY 环境变量")
    sys.exit(1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.pop("HY3_MOCK", None)

os.makedirs(os.path.join(ROOT, "demo"), exist_ok=True)
log = open(os.path.join(ROOT, "demo", "cli-e2e.txt"), "w")

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

_print("=== Hy3 CLI + 真实 API ===")
_print(f"  API: {c.api_base}")
_print(f"  模型: {c.model}")

_print("\n--- 1. 基础对话 ---")
r = c.chat([{"role": "user", "content": "你好"}], stream=False)
_print(f"  > 你好\n  < {r['content']}")
_check("非流式返回", bool(r["content"]))

_print("\n--- 2. 流式输出 ---")
chunks = list(c.chat([{"role": "user", "content": "用 Python 写一个快排"}], stream=True))
text = "".join(c["content"] for c in chunks)
_print(f"  > 用 Python 写一个快排")
_print(f"  < {len(chunks)} chunks, {len(text)} 字")
_print(f"  {'─' * 40}\n{text}\n  {'─' * 40}")
_check("流式有内容", bool(text))

_print("\n--- 3. 深度推理 ---")
r = c.chat(
    [{"role": "user", "content": "24点：3,3,8,8"}],
    stream=False,
    reasoning_effort="high",
)
_print(f"  > 24点：3,3,8,8\n  < {r['content']}")
_check("深度推理有返回", bool(r["content"]))

_print("\n--- 4. 工具调用 ---")
tools = [{"type":"function","function":{"name":"calculator","description":"计算器",
    "parameters":{"type":"object","properties":{"expr":{"type":"string"}},"required":["expr"]}}}]
r = c.chat_with_tools([{"role": "user", "content": "计算 1+1"}], tools=tools)
_print(f"  > 计算 1+1")
if r.get("tool_calls"):
    _print(f"  < 调用 {r['tool_calls'][0]['function']['name']}({r['tool_calls'][0]['function']['arguments']})")
else:
    _print(f"  < {r.get('content', '')}")
_check("有返回", bool(r.get("content") or r.get("tool_calls")))

_print("\n--- 5. 多轮对话（迭代开发通讯录） ---")
messages = []
turns = [
    "用Python写一个程序，管理个人通讯录，支持添加和查找联系人",
    "给通讯录添加删除和列出所有联系人的功能",
    "把通讯录数据保存到JSON文件，启动时自动加载",
    "用改造后的通讯录添加三个联系人，然后列出他们",
]
for i, q in enumerate(turns, 1):
    messages.append({"role": "user", "content": q})
    r = c.chat(messages, stream=False)
    content = r["content"]
    messages.append({"role": "assistant", "content": content})
    preview = content[:100].replace("\n", " ")
    _print(f"  第{i}轮 > {q}")
    _print(f"  < {preview}...")
    _check(f"第{i}轮有返回", bool(content))

_print(f"\n=== 结果: {ok}/{ok+fail} 通过, {fail} 失败 ===")
log.close()
sys.exit(0 if fail == 0 else 1)
