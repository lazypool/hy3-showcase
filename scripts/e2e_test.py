#!/usr/bin/env python3
"""
Hy3 端到端验证脚本。

使用方式：
    # Mock 模式（无需 Key）
    python scripts/e2e_test.py --mock

    # 真实 API
    export HY3_API_KEY="sk-xxxx"
    python scripts/e2e_test.py

    # 或命令行传入
    python scripts/e2e_test.py --api-key sk-xxxx
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hy3_showcase import Hy3Client

PASS = "✅ PASS"
FAIL = "❌ FAIL"

total = 0
passed = 0
failed = 0


def _pass(name, detail=""):
    global total, passed
    total += 1
    passed += 1
    print(f"  {PASS}  {name}")


def _fail(name, detail=""):
    global total, failed
    total += 1
    failed += 1
    print(f"  {FAIL}  {name}")
    if detail:
        for line in detail.strip().split("\n"):
            print(f"         {line}")


def check(name, condition, detail=""):
    (_pass if condition else _fail)(name, detail)


def check_contains(name, text, keyword):
    if keyword.lower() in text.lower():
        _pass(name)
    else:
        _fail(name, f"期望包含: {keyword}\n实际内容: {text[:200]}")


def main():
    parser = argparse.ArgumentParser(description="Hy3 端到端验证")
    parser.add_argument("--api-key", help="Hy3 API Key")
    parser.add_argument("--api-base", default=os.environ.get("HY3_API_BASE", "https://tokenhub.tencentmaas.com/v1"))
    parser.add_argument("--model", default=os.environ.get("HY3_MODEL", "hy3"))
    parser.add_argument("--mock", action="store_true", help="强制 Mock 模式")
    args = parser.parse_args()

    if args.api_key:
        os.environ["HY3_API_KEY"] = args.api_key
    if args.api_base:
        os.environ["HY3_API_BASE"] = args.api_base
    if args.model:
        os.environ["HY3_MODEL"] = args.model
    if args.mock:
        os.environ["HY3_MOCK"] = "true"

    client = Hy3Client()
    mode_str = "🔵 Mock 离线模式" if client.mock else "🟢 真实 API 模式"
    print(f"\n=== Hy3 端到端验证 ({mode_str}) ===\n")
    print(f"   API: {client.api_base}")
    print(f"   Model: {client.model}")
    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"{'─' * 60}\n")

    # ── 1. 基础对话 ──
    print("1. 基础对话（Basic Chat）")
    try:
        resp = client.chat(
            [{"role": "user", "content": "你好，请简单介绍一下你自己"}], stream=False
        )
        text = resp.to_text()
        check("非流式请求成功", bool(text and text.strip()))
        check_contains("响应包含模型介绍", text, "Hy3" if client.mock else "混元")
    except Exception as e:
         _fail(f"非流式请求失败: {e}")

    # ── 2. 多轮对话 ──
    print("\n2. 多轮对话（Multi-turn）")
    try:
        r1 = client.chat([{"role": "user", "content": "我的名字是张三"}], stream=False)
        r2 = client.chat(
            [
                {"role": "user", "content": "我的名字是张三"},
                {"role": "assistant", "content": r1.to_text()},
                {"role": "user", "content": "我刚才说了我叫什么名字？"},
            ],
            stream=False,
        )
        check("多轮对话成功", bool(r2.to_text().strip()))
    except Exception as e:
         _fail(f"多轮对话失败: {e}")

    # ── 3. 流式输出 ──
    print("\n3. 流式输出（Streaming）")
    try:
        stream = client.chat(
            [{"role": "user", "content": "用 Python 写一个快速排序"}],
            stream=True,
            reasoning_effort="no_think",
        )
        chunks = [c.content for c in stream]
        full = "".join(chunks)
        check("流式输出有内容", len(full) > 50)
        check("流式输出为逐 chunk", len(chunks) >= 2)
    except Exception as e:
         _fail(f"流式输出失败: {e}")

    # ── 4. 深度推理 ──
    print("\n4. 深度推理（Reasoning: high）")
    try:
        resp = client.chat(
            [{"role": "user", "content": "24点问题：3, 3, 8, 8 怎么算出24？"}],
            stream=False,
            reasoning_effort="high",
        )
        check("high 模式返回结果", bool(resp.to_text().strip()))
        check_contains("结果包含 24", resp.to_text(), "24")
    except Exception as e:
         _fail(f"深度推理失败: {e}")

    # ── 5. 工具调用 ──
    print("\n5. 工具调用（Tool Calling）")
    try:
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "执行数学计算",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "数学表达式",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            }
        ]
        resp = client.chat_with_tools(
            [{"role": "user", "content": "计算 (238491 * 78345) / 100 的结果"}],
            tools=tools,
            reasoning_effort="high",
        )
        check("工具调用成功", bool(resp.to_text()))
        check_contains("调用了计算器", resp.to_text(), "calculator")
    except Exception as e:
         _fail(f"工具调用失败: {e}")

    # ── 6. CLI 可用性 ──
    print("\n6. CLI 可用性（CLI Smoke Test）")
    try:
        result = subprocess.run(
            [sys.executable, "cli.py", "你好"],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ},
        )
        check("CLI 可执行", result.returncode == 0)
        check("CLI 有输出", bool(result.stdout.strip()))
    except subprocess.TimeoutExpired:
         _fail("CLI 执行超时")
    except Exception as e:
         _fail(f"CLI 执行异常: {e}")

    # ── 总结 ──
    print(f"\n{'─' * 60}")
    print(f"\n结果汇总:  {PASS} {passed}/{total}  {FAIL} {failed}/{total}\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
