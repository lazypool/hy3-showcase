import os
import gradio as gr
from hy3_showcase import Hy3Client

REASONING_OPTIONS = {
    "直接回复 (no_think)": "no_think",
    "轻度推理 (low)": "low",
    "深度推理 (high)": "high",
}

TOOLS_DEMO = [
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
                        "description": "数学表达式，如 2 + 3 * 4",
                    }
                },
                "required": ["expression"],
            },
        },
    }
]

client = Hy3Client()


def chat(message, history, reasoning_mode):
    if not message.strip():
        return "", history
    reasoning_effort = REASONING_OPTIONS[reasoning_mode]
    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    stream = client.chat(messages, stream=True, reasoning_effort=reasoning_effort)
    collected = ""
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            collected += delta.content
            yield collected, history

    history.append((message, collected))
    yield collected, history


def tool_call_demo():
    messages = [
        {"role": "user", "content": "计算 (238491 * 78345) / 100 的结果是多少？"}
    ]
    result = client.chat_with_tools(messages, tools=TOOLS_DEMO, reasoning_effort="high")
    return result


with gr.Blocks(title="Hy3 Showcase", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # Hy3 Showcase 🚀

    基于 **腾讯混元 Hy3** 模型构建的交互式演示应用。
    Hy3 是一款 295B 参数的混合专家（MoE）模型，激活参数 21B，支持 256K 上下文长度。
    """
    )

    with gr.Tab("智能对话"):
        chatbot = gr.Chatbot(label="对话", height=450)
        msg = gr.Textbox(label="输入消息", placeholder="输入你的问题...")
        with gr.Row():
            reasoning_radio = gr.Radio(
                choices=list(REASONING_OPTIONS.keys()),
                label="推理模式",
                value="直接回复 (no_think)",
            )
            clear = gr.Button("清空对话")

        gr.Markdown(
            """
        ### 提示
        - **直接回复**: "介绍一下 MoE 架构"
        - **轻度推理**: "用 Python 写一个装饰器"
        - **深度推理**: "24 点问题：3, 3, 8, 8"
        """
        )

        def respond(message, chat_history, reasoning_mode):
            result, new_history = chat(message, chat_history, reasoning_mode)
            return "", new_history

        msg.submit(respond, [msg, chatbot, reasoning_radio], [msg, chatbot])
        clear.click(lambda: None, None, chatbot, queue=False)

    with gr.Tab("工具调用演示"):
        gr.Markdown(
            """
        ### Hy3 Agent / 工具调用能力

        Hy3 支持函数调用（Function Calling），可以作为 Agent 使用。
        下面演示 Hy3 调用计算器工具完成精确数学计算。
        """
        )
        tool_output = gr.Markdown()
        run_btn = gr.Button("运行演示")
        run_btn.click(fn=tool_call_demo, outputs=tool_output)

    with gr.Tab("关于"):
        mode_status = "🟢 Mock 模式（无需 API Key）" if client.mock else "🔵 真实模式"
        gr.Markdown(
            f"""
        ### 连接信息

        | 配置 | 值 |
        |------|-----|
        | API 状态 | {mode_status} |
        | API 地址 | `{client.api_base}` |
        | 模型 | `{client.model}` |
        | 上下文长度 | 256K tokens |

        ### 环境变量

        - `HY3_API_BASE` — API 端点地址
        - `HY3_API_KEY` — API 密钥（不设置则自动进入 Mock 模式）
        - `HY3_MODEL` — 模型名称
        - `HY3_MOCK=true` — 强制 Mock 模式
        """
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
