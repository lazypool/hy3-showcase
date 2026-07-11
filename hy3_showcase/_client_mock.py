"""Mock 后端实现 — 无需 API Key，关键词驱动。"""
from . import _mock_data
from .models import ChatResponse, StreamChunk, ToolCall
from .protocol import Hy3Backend, StreamIterator


class MockBackend(Hy3Backend):
    def __init__(self, api_base: str, model: str):
        self.api_base = api_base
        self.model = model

    def chat(self, messages, temperature=0.7, reasoning_effort="no_think"):
        content = _mock_data.select_content(messages, reasoning_effort)
        return ChatResponse(content=content)

    def chat_stream(self, messages, temperature=0.7, reasoning_effort="no_think"):
        content = _mock_data.select_content(messages, reasoning_effort)
        step = 5
        chunks = [
            StreamChunk(content=content[i : i + step])
            for i in range(0, len(content), step)
        ]
        return StreamIterator(chunks)

    def chat_with_tools(self, messages, tools=None, reasoning_effort="no_think"):
        name, args = _mock_data.select_tool_call(messages)
        return ChatResponse(
            tool_calls=[ToolCall(function_name=name, arguments=args)],
            is_tool_call=True,
        )
