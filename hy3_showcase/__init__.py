"""Hy3 Showcase — 统一入口。

使用方式：
    from hy3_showcase import create_client

    client = create_client()
    resp = client.chat([{"role": "user", "content": "你好"}])
    print(resp.to_text())
"""
from ._client_mock import MockBackend
from ._client_real import RealBackend
from .config import load_config
from .errors import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    Hy3Error,
    MockOnlyFeature,
    RateLimitError,
)
from .models import ChatResponse, StreamChunk, ToolCall


class Hy3Client:
    """Hy3 客户端门面（Facade）。

    自动根据配置选择 RealBackend 或 MockBackend，
    对外暴露统一的高层 API。
    """

    def __init__(self):
        config = load_config()
        self.api_base = config["api_base"]
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.mock = config["mock"]

        if self.mock:
            self._backend = MockBackend(self.api_base, self.model)
        else:
            self._backend = RealBackend(self.api_base, self.api_key, self.model)

    def chat(self, messages, temperature=0.7, stream=False, reasoning_effort="no_think"):
        if stream:
            return self._backend.chat_stream(messages, temperature, reasoning_effort)
        return self._backend.chat(messages, temperature, reasoning_effort)

    def chat_with_tools(self, messages, tools=None, reasoning_effort="no_think"):
        return self._backend.chat_with_tools(messages, tools, reasoning_effort)


def create_client() -> Hy3Client:
    """创建 Hy3 客户端实例。"""
    return Hy3Client()


__all__ = [
    "Hy3Client",
    "create_client",
    "ChatResponse",
    "StreamChunk",
    "ToolCall",
    "Hy3Error",
    "ConfigurationError",
    "ConnectionError",
    "AuthenticationError",
    "RateLimitError",
    "MockOnlyFeature",
]
