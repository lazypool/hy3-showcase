"""Hy3 Mock 响应数据与生成逻辑。"""

MOCK_REPLIES = {
    "你是谁 介绍自己 who are you": (
        "我是 **Hy3**，由腾讯混元团队研发的快慢思考融合混合专家模型（MoE）。"
        "我有 295B 总参数量、21B 激活参数，支持 256K 上下文，"
        "具备强大的推理、Agent 和工具调用能力。"
    ),
    "快速排序 快排 quicksort": (
        "以下是 Python 快速排序实现：\n\n"
        "```python\ndef quicksort(arr):\n"
        "    if len(arr) <= 1:\n        return arr\n"
        "    pivot = arr[len(arr) // 2]\n"
        "    left = [x for x in arr if x < pivot]\n"
        "    middle = [x for x in arr if x == pivot]\n"
        "    right = [x for x in arr if x > pivot]\n"
        "    return quicksort(left) + middle + quicksort(right)\n```"
    ),
    "moe 混合专家 架构": (
        "**MoE（Mixture of Experts，混合专家）** 是一种神经网络架构，"
        "它将模型拆分为多个「专家」子网络，每个输入只激活其中一部分专家。\n\n"
        "Hy3 包含 192 个专家，每次激活 top-8，参数量 295B 但激活仅 21B。"
        "这使得模型兼具大容量和高效率。"
    ),
    "你好 hello hi": "你好！我是 Hy3，有什么可以帮助你的吗？",
    "python 装饰器": (
        "以下是一个 Python 装饰器示例：\n\n"
        "```python\nimport time\n\ndef timer(func):\n"
        "    def wrapper(*args, **kwargs):\n        start = time.time()\n"
        "        result = func(*args, **kwargs)\n"
        "        print(f'耗时: {time.time()-start:.3f}秒')\n"
        "        return result\n    return wrapper\n\n"
        "@timer\ndef f():\n    time.sleep(1)\n    return 'ok'\n```"
    ),
    "24点": "8 ÷ (3 - 8 ÷ 3) = 8 ÷ (3 - 2.667) = 8 ÷ 0.333 = 24",
    "flask web 待办": (
        "```python\nfrom flask import Flask, request, jsonify\n\n"
        "app = Flask(__name__)\ntodos = []\n\n"
        '@app.route("/todos", methods=["GET"])\n'
        "def list():\n    return jsonify(todos)\n\n"
        '@app.route("/todos", methods=["POST"])\n'
        "def add():\n    t = request.json\n    todos.append(t)\n"
        "    return jsonify(t), 201\n\n"
        'if __name__ == "__main__":\n    app.run()\n```'
    ),
    "分布式 缓存": (
        "## 分布式缓存设计要点\n\n"
        "**分片**：一致性哈希 + 虚拟节点\n"
        "**高可用**：主从复制 + Raft 故障转移\n"
        "**淘汰**：LRU / LFU / TTL\n"
        "**方案**：Redis Cluster / Codis"
    ),
}

MOCK_REASONING = (
    "**【推理过程】**\n\n"
    "1. 分析问题\n2. 拆分子问题\n3. 逐步推导\n4. 综合结论\n\n"
    "**【最终回答】**\n经过推理："
)


def mock_reply(messages, reasoning_effort="no_think"):
    prompt = " ".join(m["content"] for m in messages if m["role"] == "user").lower()

    if any(k in prompt for k in ["计算", "计算器", "calculator", "运算"]):
        if "238491" in prompt:
            return {
                "content": None,
                "tool_calls": [
                    {
                        "function": {
                            "name": "calculator",
                            "arguments": '{"expression": "(238491 * 78345) / 100"}',
                        }
                    }
                ],
            }
        return {
            "content": None,
            "tool_calls": [
                {
                    "function": {
                        "name": "calculator",
                        "arguments": '{"expression": "运算表达式"}',
                    }
                }
            ],
        }

    if reasoning_effort == "high":
        if "24" in prompt and "点" in prompt:
            return {"content": "8 ÷ (3 - 8 ÷ 3) = 24 ✅"}
        return {"content": MOCK_REASONING}

    for keywords, reply in MOCK_REPLIES.items():
        if any(k.strip() in prompt for k in keywords.split()):
            return {"content": reply}

    return {"content": f"收到：{messages[-1]['content']}"}


class MockStream:
    def __init__(self, text):
        self._idx = 0
        self._text = text

    def __iter__(self):
        return self

    def __next__(self):
        if self._idx >= len(self._text):
            raise StopIteration
        end = min(self._idx + 5, len(self._text))
        chunk = self._text[self._idx:end]
        self._idx = end
        return {"content": chunk}
