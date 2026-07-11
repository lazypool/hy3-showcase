#!/usr/bin/env python3
import argparse
from hy3_showcase import Hy3Client


def main():
    client = Hy3Client()
    p = argparse.ArgumentParser(description="Hy3 CLI")
    p.add_argument("prompt", nargs="?", help="输入提示")
    p.add_argument("--reasoning", choices=["no_think", "low", "high"], default="no_think")
    p.add_argument("--stream", action="store_true")
    args = p.parse_args()

    mode = "Mock" if client.mock else "Real"
    print(f"Hy3 CLI ({mode})  {client.api_base}  {client.model}\n")

    if args.prompt:
        msgs = [{"role": "user", "content": args.prompt}]
        if args.stream:
            for ch in client.chat(msgs, stream=True, reasoning_effort=args.reasoning):
                print(ch["content"], end="", flush=True)
            print()
        else:
            r = client.chat(msgs, stream=False, reasoning_effort=args.reasoning)
            print(r.get("content", ""))
        return

    print("交互模式（/exit 退出）")
    while True:
        try:
            s = input("\n>>> ")
            if s.lower() in ("/exit", "/quit"):
                break
            r = client.chat([{"role": "user", "content": s}], stream=False)
            print(r.get("content", ""))
        except KeyboardInterrupt:
            print()
            break


if __name__ == "__main__":
    main()
