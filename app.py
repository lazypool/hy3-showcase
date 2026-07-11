import gradio as gr
from hy3_showcase import Hy3Client

REASONING = {
    "直接回复": "no_think",
    "轻度推理": "low",
    "深度推理": "high",
}

TOOLS = [{
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
}]

client = Hy3Client()


def tool_demo():
    resp = client.chat_with_tools(
        [{"role": "user", "content": "计算 (238491 * 78345) / 100 的结果是多少？"}],
        tools=TOOLS, reasoning_effort="high",
    )
    tc = resp.get("tool_calls")
    if tc:
        parts = ["**调用了工具：**\n"]
        for t in tc:
            parts.append(f"- {t['function']['name']}: {t['function']['arguments']}\n")
        return "".join(parts)
    return resp.get("content", "")


with gr.Blocks(title="Hy3 Showcase") as demo:
    gr.Markdown("# Hy3 Showcase\n基于腾讯混元 Hy3 模型的交互演示。")

    with gr.Tab("对话"):
        bot = gr.Chatbot(height=450)
        msg = gr.Textbox(placeholder="输入问题...")
        with gr.Row():
            mode = gr.Radio(choices=list(REASONING), label="推理模式", value="直接回复")
            clear = gr.Button("清空")

        gr.Markdown("**提示**：「介绍一下 MoE 架构」/ 「快排」/ 「24 点：3,3,8,8」")

        def respond(m, h, r):
            if not m.strip():
                yield "", h
                return
            h.append({"role": "user", "content": m})
            msgs = [{"role": msg["role"], "content": msg["content"]} for msg in h]
            collected = ""
            for chunk in client.chat(msgs, stream=True, reasoning_effort=REASONING[r]):
                collected += chunk["content"]
                yield "", h + [{"role": "assistant", "content": collected}]
            yield "", h + [{"role": "assistant", "content": collected}]

        msg.submit(respond, [msg, bot, mode], [msg, bot])
        clear.click(lambda: None, None, bot)

    with gr.Tab("工具调用"):
        gr.Markdown("### Agent 演示\nHy3 调用计算器工具完成数学计算。")
        out = gr.Markdown()
        gr.Button("运行").click(fn=tool_demo, outputs=out)

    with gr.Tab("关于"):
        status = "Mock（离线）" if client.mock else "真实 API"
        gr.Markdown(
            f"**状态**: {status}\n\n"
            f"**API**: {client.api_base}\n\n"
            f"**模型**: {client.model}\n\n"
            "环境变量：`HY3_API_BASE` / `HY3_API_KEY` / `HY3_MODEL` / `HY3_MOCK`"
        )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())
