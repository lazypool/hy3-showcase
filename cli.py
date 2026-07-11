import argparse
import os
from openai import OpenAI


def create_client():
    return OpenAI(
        base_url=os.environ.get("HY3_API_BASE", "http://localhost:8000/v1"),
        api_key=os.environ.get("HY3_API_KEY", "EMPTY"),
    )


def chat(prompt, reasoning_effort="no_think", stream=False, model=None):
    client = create_client()
    model = model or os.environ.get("HY3_MODEL", "hy3")
    extra_body = {"chat_template_kwargs": {"reasoning_effort": reasoning_effort}}

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=stream,
        extra_body=extra_body,
    )

    if stream:
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
        print()
    else:
        print(response.choices[0].message.content)


def main():
    parser = argparse.ArgumentParser(description="Hy3 命令行聊天客户端")
    parser.add_argument("prompt", nargs="?", help="输入提示")
    parser.add_argument("--reasoning", choices=["no_think", "low", "high"], default="no_think")
    parser.add_argument("--stream", action="store_true", help="流式输出")
    parser.add_argument("--model", default=None, help="模型名称")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互模式")

    args = parser.parse_args()

    if args.interactive:
        print("Hy3 交互模式（输入 /exit 退出）")
        while True:
            try:
                user_input = input("\n>>> ")
                if user_input.lower() in ("/exit", "/quit"):
                    break
                chat(user_input, args.reasoning, args.stream, args.model)
            except KeyboardInterrupt:
                print("\n再见！")
                break
    elif args.prompt:
        chat(args.prompt, args.reasoning, args.stream, args.model)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
