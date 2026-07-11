from abc import ABC, abstractmethod
from typing import Optional

from .models import ChatResponse, StreamChunk


class Hy3Backend(ABC):
    """Hy3 API 后端抽象接口。"""

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        reasoning_effort: str = "no_think",
    ) -> ChatResponse:
        ...

    @abstractmethod
    def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        reasoning_effort: str = "no_think",
    ) -> "StreamIterator":
        ...

    @abstractmethod
    def chat_with_tools(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        reasoning_effort: str = "no_think",
    ) -> ChatResponse:
        ...


class StreamIterator:
    """流式迭代器抽象，支持逐 chunk 消费。"""

    def __init__(self, chunks: list[StreamChunk]):
        self._chunks = chunks
        self._idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._idx >= len(self._chunks):
            raise StopIteration
        chunk = self._chunks[self._idx]
        self._idx += 1
        return chunk
