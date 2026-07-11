"""Hy3 API 客户端 — 自动切换真实 API 和 Mock 离线模式。"""
from openai import OpenAI

from .config import load_config
from .mock import mock_reply, MockStream


class Hy3Client:
    def __init__(self):
        cfg = load_config()
        self.api_base = cfg["api_base"]
        self.api_key = cfg["api_key"]
        self.model = cfg["model"]
        self.mock = cfg["mock"]
        if not self.mock:
            self._cli = OpenAI(base_url=self.api_base, api_key=self.api_key)

    def chat(self, messages, temperature=0.7, stream=False, reasoning_effort="no_think"):
        if self.mock:
            reply = mock_reply(messages, reasoning_effort)
            if stream:
                return MockStream(reply.get("content") or "")
            return reply

        extra = {"chat_template_kwargs": {"reasoning_effort": reasoning_effort}}
        resp = self._cli.chat.completions.create(
            model=self.model, messages=messages,
            temperature=temperature, stream=stream, extra_body=extra,
        )
        if stream:
            return _StreamWrapper(resp)
        return _wrap(resp)

    def chat_with_tools(self, messages, tools=None, reasoning_effort="no_think"):
        if self.mock:
            return mock_reply(messages, reasoning_effort)
        resp = self._cli.chat.completions.create(
            model=self.model, messages=messages, tools=tools or [],
            temperature=0.7,
            extra_body={"chat_template_kwargs": {"reasoning_effort": reasoning_effort}},
        )
        return _wrap(resp)


def _wrap(resp):
    msg = resp.choices[0].message
    if msg.tool_calls:
        return {
            "content": None,
            "tool_calls": [
                {"function": {"name": t.function.name, "arguments": t.function.arguments}}
                for t in msg.tool_calls
            ],
        }
    return {"content": msg.content}


class _StreamWrapper:
    def __init__(self, stream):
        self._it = iter(stream)

    def __iter__(self):
        return self

    def __next__(self):
        chunk = next(self._it)
        d = chunk.choices[0].delta
        return {"content": d.content or ""}
