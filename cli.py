#!/usr/bin/env python3
import argparse
from hy3_showcase import Hy3Client


def main():
    client = Hy3Client()

    parser = argparse.ArgumentParser(description="Hy3 命令行聊天客户端")
    parser.add_argument("prompt", nargs="?", help="输入提示")
    parser.add_argument("--reasoning", choices=["no_think", "low", "high"], default="no_think")
    parser.add_argument("--stream", action="store_true", help="流式输出")

    args = parser.parse_args()

    mode = "🔵 Mock" if client.mock else "🟢 真实"
    print(f"=== Hy3 CLI ({mode} 模式) ===")
    print(f"    API: {client.api_base}  Model: {client.model}\n")

    if args.prompt:
        messages = [{"role": "user", "content": args.prompt}]
        if args.stream:
            print("--- 流式输出 ---")
            for chunk in client.chat(messages, stream=True, reasoning_effort=args.reasoning):
                print(chunk.content, end="", flush=True)
            print()
        else:
            resp = client.chat(messages, stream=False, reasoning_effort=args.reasoning)
            print(resp.to_text())
        return

    print("交互模式（输入 /exit 退出）")
    while True:
        try:
            user_input = input("\n>>> ")
            if user_input.lower() in ("/exit", "/quit"):
                break
            messages = [{"role": "user", "content": user_input}]
            resp = client.chat(messages, stream=False, reasoning_effort="no_think")
            print(resp.to_text())
        except KeyboardInterrupt:
            print("\n再见！")
            break


if __name__ == "__main__":
    main()
