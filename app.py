import os
import gradio as gr
from openai import OpenAI


HY3_API_BASE = os.environ.get("HY3_API_BASE", "http://localhost:8000/v1")
HY3_API_KEY = os.environ.get("HY3_API_KEY", "EMPTY")
HY3_MODEL = os.environ.get("HY3_MODEL", "hy3")

REASONING_OPTIONS = {
    "直接回复 (no_think)": "no_think",
    "轻度推理 (low)": "low",
    "深度推理 (high)": "high",
}


def get_client():
    return OpenAI(base_url=HY3_API_BASE, api_key=HY3_API_KEY)


def chat(message, history, reasoning_mode):
    client = get_client()
    reasoning_effort = REASONING_OPTIONS[reasoning_mode]

    messages = []
    for h in history:
        messages.append({"role": "user", "content": h[0]})
        messages.append({"role": "assistant", "content": h[1]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=HY3_MODEL,
        messages=messages,
        temperature=0.7,
        stream=True,
        extra_body={
            "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
        },
    )

    collected = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        if delta.content:
            collected += delta.content
            yield collected


def tool_call_demo():
    client = get_client()
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
                            "description": "数学表达式，如 2 + 3 * 4",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model=HY3_MODEL,
        messages=[
            {
                "role": "user",
                "content": "计算 (238491 * 78345) / 100 的结果是多少？",
            }
        ],
        tools=tools,
        temperature=0.7,
        extra_body={
            "chat_template_kwargs": {"reasoning_effort": "high"}
        },
    )

    msg = response.choices[0].message
    if msg.tool_calls:
        result = "**Hy3 调用了工具：**\n\n"
        for tc in msg.tool_calls:
            result += f"- 函数: {tc.function.name}\n"
            result += f"- 参数: {tc.function.arguments}\n"
        return result
    else:
        return f"**回复：**\n\n{msg.content}"


with gr.Blocks(title="Hy3 Showcase", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
    # Hy3 Showcase 🚀

    基于 **腾讯混元 Hy3** 模型构建的交互式演示应用。Hy3 是一款 295B 参数的混合专家（MoE）模型，激活参数 21B，支持 256K 上下文长度。
    """
    )

    with gr.Tab("智能对话"):
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="对话", height=500)
                msg = gr.Textbox(label="输入消息", placeholder="输入你的问题...")
                with gr.Row():
                    reasoning_radio = gr.Radio(
                        choices=list(REASONING_OPTIONS.keys()),
                        label="推理模式",
                        value="直接回复 (no_think)",
                    )
                    clear = gr.Button("清空对话")
            with gr.Column(scale=1):
                gr.Markdown(
                    """
                ### 推理模式说明

                - **no_think**: 直接回复，适合日常问答
                - **low**: 轻度推理，适合中等复杂任务
                - **high**: 深度思维链推理，适合数学、编程、逻辑推理

                ### 提示

                试试以下问题体验不同模式：
                - "用 Python 写一个快排"
                - "解释什么是 MoE 架构"
                - "24 点问题：3, 3, 8, 8"
                """
                )

        def respond(message, chat_history, reasoning_mode):
            if not message.strip():
                return "", chat_history
            bot_message = ""
            for partial in chat(message, chat_history, reasoning_mode):
                bot_message = partial
            chat_history.append((message, bot_message))
            return "", chat_history

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
        gr.Markdown(
            f"""
        ### 连接信息

        | 配置 | 值 |
        |------|-----|
        | API 地址 | `{HY3_API_BASE}` |
        | 模型 | `{HY3_MODEL}` |
        | 上下文长度 | 256K tokens |
        | 总参数量 | 295B (MoE) |
        | 激活参数量 | 21B |

        ### 部署指南

        请参考 [Hy3 README](https://github.com/Tencent-Hunyuan/Hy3) 了解部署方式。
        """
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
