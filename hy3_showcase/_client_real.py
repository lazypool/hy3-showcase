"""OpenAI 兼容 API 后端实现。"""
import importlib

from .errors import AuthenticationError, ConnectionError, RateLimitError
from .models import ChatResponse, StreamChunk, ToolCall
from .protocol import Hy3Backend, StreamIterator

_openai = importlib.import_module("openai")


class RealBackend(Hy3Backend):
    def __init__(self, api_base: str, api_key: str, model: str):
        self.api_base = api_base
        self.model = model
        self._client = _openai.OpenAI(base_url=api_base, api_key=api_key)

    def chat(self, messages, temperature=0.7, reasoning_effort="no_think"):
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=False,
                extra_body={
                    "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
                },
            )
        except _openai.APIStatusError as e:
            if e.status_code == 401:
                raise AuthenticationError(f"API Key 无效: {e}") from e
            if e.status_code == 429:
                raise RateLimitError(f"请求被限流: {e}") from e
            raise ConnectionError(f"API 返回错误 {e.status_code}: {e}") from e
        except _openai.APIConnectionError as e:
            raise ConnectionError(f"无法连接到 {self.api_base}: {e}") from e

        msg = response.choices[0].message
        return self._to_response(msg)

    def chat_stream(self, messages, temperature=0.7, reasoning_effort="no_think"):
        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
                extra_body={
                    "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
                },
            )
        except _openai.APIStatusError as e:
            if e.status_code == 401:
                raise AuthenticationError(f"API Key 无效: {e}") from e
            if e.status_code == 429:
                raise RateLimitError(f"请求被限流: {e}") from e
            raise ConnectionError(f"API 返回错误 {e.status_code}: {e}") from e
        except _openai.APIConnectionError as e:
            raise ConnectionError(f"无法连接到 {self.api_base}: {e}") from e

        chunks = []
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                chunks.append(StreamChunk(content=delta.content))
        return StreamIterator(chunks)

    def chat_with_tools(self, messages, tools=None, reasoning_effort="no_think"):
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools or [],
                temperature=0.7,
                extra_body={
                    "chat_template_kwargs": {"reasoning_effort": reasoning_effort}
                },
            )
        except _openai.APIStatusError as e:
            if e.status_code == 401:
                raise AuthenticationError(f"API Key 无效: {e}") from e
            raise ConnectionError(f"API 返回错误 {e.status_code}: {e}") from e
        except _openai.APIConnectionError as e:
            raise ConnectionError(f"无法连接到 {self.api_base}: {e}") from e

        msg = response.choices[0].message
        return self._to_response(msg)

    def _to_response(self, msg) -> ChatResponse:
        if msg.tool_calls:
            calls = [
                ToolCall(function_name=tc.function.name, arguments=tc.function.arguments)
                for tc in msg.tool_calls
            ]
            return ChatResponse(tool_calls=calls, is_tool_call=True)
        return ChatResponse(content=msg.content)
