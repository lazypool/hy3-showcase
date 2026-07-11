"""Hy3 API client with mock fallback.

当 HY3_API_KEY 未设置或 HY3_MOCK=true 时自动使用 mock 模式，
无需真实 API 端点即可体验完整交互流程。
"""
import json
import os
import re
import importlib

from .config import load_config

_openai = importlib.import_module("openai")


def _mock_chat(messages, reasoning_effort="no_think"):
    """关键词驱动的 mock 响应，模拟 Hy3 各能力维度。"""
    prompt = ""
    for m in messages:
        if m["role"] == "user":
            prompt += m["content"] + " "

    p = prompt.lower()

    # 检测工具调用意图
    if any(k in p for k in ["计算", "计算器", "数学", "加减乘除", "calculator", "运算"]):
        return _mock_tool_call(p)

    # 检测推理模式
    if reasoning_effort == "high":
        return _mock_reasoning_response(p)

    # 对话类响应
    if any(k in p for k in ["你是谁", "介绍", "介绍自己", "who are you"]):
        return (
            "我是 **Hy3**，由腾讯混元团队研发的快慢思考融合混合专家模型（MoE）。"
            "我有 295B 总参数量、21B 激活参数，支持 256K 上下文，"
            "具备强大的推理、Agent 和工具调用能力。"
        )
    if any(k in p for k in ["快速排序", "快排", "quicksort", "排序算法"]):
        return (
            "以下是 Python 快速排序实现：\n\n"
            "```python\ndef quicksort(arr):\n"
            '    if len(arr) <= 1:\n        return arr\n'
            "    pivot = arr[len(arr) // 2]\n"
            "    left = [x for x in arr if x < pivot]\n"
            "    middle = [x for x in arr if x == pivot]\n"
            "    right = [x for x in arr if x > pivot]\n"
            "    return quicksort(left) + middle + quicksort(right)\n```"
        )
    if any(k in p for k in ["moE", "混合专家", "混合专家模型", "架构"]):
        return (
            "**MoE（Mixture of Experts，混合专家）** 是一种神经网络架构，"
            "它将模型拆分为多个「专家」子网络，每个输入只激活其中一部分专家。\n\n"
            "Hy3 包含 192 个专家，每次激活 top-8，参数量 295B 但激活仅 21B。"
            "这使得模型兼具大容量和高效率。"
        )
    if any(k in p for k in ["分布式", "缓存系统", "设计"]):
        return (
            "## 分布式缓存系统设计要点\n\n"
            "**1. 数据分片**\n- 一致性哈希：解决扩缩容时的数据迁移问题\n"
            "- 虚拟节点：均衡负载分布\n\n"
            "**2. 高可用**\n- 主从复制（Leader/Follower）\n"
            "- Sentinel 或 Raft 协议实现自动故障转移\n\n"
            "**3. 淘汰策略**\n- LRU / LFU / TTL 过期\n- 内存上限保护\n\n"
            "**4. 常见方案**\n- Redis Cluster / Codis / Twemproxy"
        )
    if any(k in p for k in ["你好", "hello", "hi", "嗨"]):
        return "你好！我是 Hy3，有什么可以帮助你的吗？"
    if any(k in p for k in ["python", "装饰器", "decorator"]):
        return (
            "以下是一个 Python 装饰器示例：\n\n"
            "```python\nimport time\n\ndef timer(func):\n"
            '    def wrapper(*args, **kwargs):\n'
            "        start = time.time()\n"
            "        result = func(*args, **kwargs)\n"
            f"        print(f'执行耗时: {{time.time()-start:.3f}}秒')\n"
            "        return result\n    return wrapper\n\n"
            "@timer\ndef slow_function():\n    time.sleep(1)\n    return '完成'\n```"
        )
    if any(k in p for k in ["24点", "24 点", "3, 3, 8, 8"]):
        return "8 ÷ (3 - 8 ÷ 3) = 8 ÷ (3 - 2.667) = 8 ÷ 0.333 = 24"
    if any(k in p for k in ["flask", "web应用", "web 应用", "待办"]):
        return (
            "```python\nfrom flask import Flask, request, jsonify\n\n"
            "app = Flask(__name__)\ntodos = []\n\n"
            '@app.route("/todos", methods=["GET"])\n'
            "def list_todos():\n    return jsonify(todos)\n\n"
            '@app.route("/todos", methods=["POST"])\n'
            "def add_todo():\n    todo = request.json\n"
            "    todos.append(todo)\n    return jsonify(todo), 201\n\n"
            'if __name__ == "__main__":\n    app.run(debug=True)\n```'
        )

    return (
        f"收到你的消息：「{messages[-1]['content']}」。"
        "我是一个 AI 助手，可以帮你解答问题、编写代码、进行推理分析等。"
        "请问有什么可以帮你的？"
    )


def _mock_reasoning_response(prompt):
    return (
        "**【推理过程】**\n\n"
        "1. 分析问题：这是一个需要深度推理的问题\n"
        "2. 分解子问题：拆解为多个可处理的部分\n"
        "3. 逐步推理：每一步基于前一步的结论\n"
        "4. 综合结论：将各子问题的解合并\n\n"
        "**【最终回答】**\n\n"
        "经过逐步推理，以下是完整的解决方案：\n\n"
        "对于复杂问题，'high' 模式会先展示思维链再给出答案。"
    )


def _mock_tool_call(prompt):
    params = {"expression": "unknown"}
    if "238491" in prompt:
        params = {"expression": "(238491 * 78345) / 100"}
    elif "*" in prompt or "乘" in prompt:
        params = {"expression": "运算表达式"}
    result = (
        "**Hy3 调用了计算器工具：**\n\n"
        f"- 函数: calculator\n"
        f"- 参数: {json.dumps(params)}"
    )
    return result


class Hy3Client:
    def __init__(self):
        config = load_config()
        self.api_base = config["api_base"]
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.mock = config["mock"]
        if not self.mock:
            self._client = _openai.OpenAI(
                base_url=self.api_base,
                api_key=self.api_key,
            )

    def chat(self, messages, temperature=0.7, stream=False, reasoning_effort="no_think"):
        if self.mock:
            return self._mock_chat_stream(messages, reasoning_effort, stream)

        extra_body = {
            "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
        }
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=stream,
            extra_body=extra_body,
        )
        return response

    def _mock_chat_stream(self, messages, reasoning_effort, stream):
        content = _mock_chat(messages, reasoning_effort)

        if stream:

            class MockStream:
                def __init__(self, text):
                    self._text = text
                    self._idx = 0

                def __iter__(self):
                    return self

                def __next__(self):
                    if self._idx >= len(self._text):
                        raise StopIteration
                    chunk_size = min(5, len(self._text) - self._idx)
                    chunk = self._text[self._idx:self._idx + chunk_size]
                    self._idx += chunk_size
                    return type('Chunk', (), {
                        'choices': [type('Choice', (), {
                            'delta': type('Delta', (), {'content': chunk})()
                        })()]
                    })()

            return MockStream(content)
        else:
            return type('Response', (), {
                'choices': [type('Choice', (), {
                    'message': type('Msg', (), {'content': content})()
                })()]
            })()

    def chat_with_tools(self, messages, tools=None, reasoning_effort="no_think"):
        if self.mock:
            content = _mock_chat(messages, reasoning_effort)
            return content

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or [],
            temperature=0.7,
            extra_body={
                "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
            },
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            result = "**Hy3 调用了工具：**\n\n"
            for tc in msg.tool_calls:
                result += f"- 函数: {tc.function.name}\n"
                result += f"- 参数: {tc.function.arguments}\n"
            return result
        return msg.content
