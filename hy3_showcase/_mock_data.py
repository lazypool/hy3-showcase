"""Mock 响应内容库 — 关键词匹配 → 预置回复。

与 Mock 客户端分离，方便增删场景而不影响客户端逻辑。
"""


def select_content(messages: list[dict], reasoning_effort: str = "no_think") -> str:
    prompt = _build_prompt(messages)
    p = prompt.lower()

    if _match_tool_call(p):
        return _tool_call_content(p)
    if reasoning_effort == "high":
        return _reasoning_content(p)
    return _chat_content(p, messages)


def select_tool_call(messages: list[dict]) -> "tuple[str, str]":
    prompt = _build_prompt(messages)
    p = prompt.lower()
    if "238491" in p:
        return "calculator", '{"expression": "(238491 * 78345) / 100"}'
    return "calculator", '{"expression": "运算表达式"}'


def _build_prompt(messages: list[dict]) -> str:
    return " ".join(m["content"] for m in messages if m["role"] == "user")


def _match_tool_call(p: str) -> bool:
    return any(k in p for k in ["计算", "计算器", "数学", "加减乘除", "calculator", "运算"])


def _tool_call_content(p: str) -> str:
    if "238491" in p:
        return (
            "**Hy3 调用了计算器工具：**\n\n"
            "- 函数: calculator\n"
            '- 参数: {"expression": "(238491 * 78345) / 100"}\n'
        )
    return (
        "**Hy3 调用了计算器工具：**\n\n"
        "- 函数: calculator\n"
        '- 参数: {"expression": "运算表达式"}\n'
    )


def _reasoning_content(p: str) -> str:
    if "24" in p and "点" in p:
        return (
            "**【推理过程】**\n\n"
            "1. 分析问题：需要从 3, 3, 8, 8 四个数字通过四则运算得到 24\n"
            "2. 尝试组合：8 × 3 = 24，剩余 3 和 8 无法消去\n"
            "3. 尝试除法：8 ÷ 3 ≈ 2.667，3 - 2.667 = 0.333，8 ÷ 0.333 = 24\n"
            "4. 验证：8 ÷ (3 - 8 ÷ 3) = 24 ✅\n\n"
            "**【最终回答】**\n\n"
            "8 ÷ (3 - 8 ÷ 3) = 24"
        )
    return (
        "**【推理过程】**\n\n"
        "1. 分析问题：这是一个需要深度推理的问题\n"
        "2. 分解子问题：拆解为多个可处理的部分\n"
        "3. 逐步推理：每一步基于前一步的结论\n"
        "4. 综合结论：将各子问题的解合并\n\n"
        "**【最终回答】**\n\n"
        "经过逐步推理，以下是完整的解决方案。"
    )


def _chat_content(p: str, messages: list[dict]) -> str:
    SCENARIOS: list[tuple[list[str], str]] = [
        (["你是谁", "介绍自己", "who are you"],
         "我是 **Hy3**，由腾讯混元团队研发的快慢思考融合混合专家模型（MoE）。"
         "我有 295B 总参数量、21B 激活参数，支持 256K 上下文，"
         "具备强大的推理、Agent 和工具调用能力。"),
        (["快速排序", "快排", "quicksort", "排序算法"],
         "以下是 Python 快速排序实现：\n\n"
         "```python\ndef quicksort(arr):\n"
         "    if len(arr) <= 1:\n        return arr\n"
         "    pivot = arr[len(arr) // 2]\n"
         "    left = [x for x in arr if x < pivot]\n"
         "    middle = [x for x in arr if x == pivot]\n"
         "    right = [x for x in arr if x > pivot]\n"
         "    return quicksort(left) + middle + quicksort(right)\n```"),
        (["moE", "混合专家", "混合专家模型", "架构"],
         "**MoE（Mixture of Experts，混合专家）** 是一种神经网络架构，"
         "它将模型拆分为多个「专家」子网络，每个输入只激活其中一部分专家。\n\n"
         "Hy3 包含 192 个专家，每次激活 top-8，参数量 295B 但激活仅 21B。"
         "这使得模型兼具大容量和高效率。"),
        (["分布式", "缓存系统", "设计"],
         "## 分布式缓存系统设计要点\n\n"
         "**1. 数据分片**\n- 一致性哈希：解决扩缩容时的数据迁移问题\n"
         "- 虚拟节点：均衡负载分布\n\n"
         "**2. 高可用**\n- 主从复制（Leader/Follower）\n"
         "- Sentinel 或 Raft 协议实现自动故障转移\n\n"
         "**3. 淘汰策略**\n- LRU / LFU / TTL 过期\n- 内存上限保护\n\n"
         "**4. 常见方案**\n- Redis Cluster / Codis / Twemproxy"),
        (["你好", "hello", "hi", "嗨"],
         "你好！我是 Hy3，有什么可以帮助你的吗？"),
        (["python", "装饰器", "decorator"],
         "以下是一个 Python 装饰器示例：\n\n"
         "```python\nimport time\n\ndef timer(func):\n"
         "    def wrapper(*args, **kwargs):\n"
         "        start = time.time()\n"
         "        result = func(*args, **kwargs)\n"
         "        print(f'执行耗时: {time.time()-start:.3f}秒')\n"
         "        return result\n    return wrapper\n\n"
         "@timer\ndef slow_function():\n    time.sleep(1)\n    return '完成'\n```"),
        (["24点", "24 点", "3, 3, 8, 8"],
         "8 ÷ (3 - 8 ÷ 3) = 8 ÷ (3 - 2.667) = 8 ÷ 0.333 = 24"),
        (["flask", "web应用", "待办"],
         "```python\nfrom flask import Flask, request, jsonify\n\n"
         "app = Flask(__name__)\ntodos = []\n\n"
         '@app.route("/todos", methods=["GET"])\n'
         "def list_todos():\n    return jsonify(todos)\n\n"
         '@app.route("/todos", methods=["POST"])\n'
         "def add_todo():\n    todo = request.json\n"
         "    todos.append(todo)\n    return jsonify(todo), 201\n\n"
         'if __name__ == "__main__":\n    app.run(debug=True)\n```'),
    ]

    for keywords, reply in SCENARIOS:
        if any(k in p for k in keywords):
            return reply

    last = messages[-1]["content"] if messages else ""
    return (
        f"收到你的消息：「{last}」。"
        "我是一个 AI 助手，可以帮你解答问题、编写代码、进行推理分析等。"
        "请问有什么可以帮你的？"
    )
