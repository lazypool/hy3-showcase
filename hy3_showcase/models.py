from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Delta:
    content: Optional[str] = None


@dataclass
class Choice:
    delta: Optional[Delta] = None
    message: Optional["Message"] = None
    index: int = 0


@dataclass
class Message:
    content: Optional[str] = None
    role: str = "assistant"
    tool_calls: Optional[list] = None


@dataclass
class ToolCall:
    function_name: str = ""
    arguments: str = ""


@dataclass
class ChatResponse:
    """统一响应模型，Real 和 Mock 共用。"""
    content: Optional[str] = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    is_tool_call: bool = False

    def to_text(self) -> str:
        if self.is_tool_call:
            parts = ["**Hy3 调用了工具：**\n"]
            for tc in self.tool_calls:
                parts.append(f"- 函数: {tc.function_name}\n")
                parts.append(f"- 参数: {tc.arguments}\n")
            return "".join(parts)
        return self.content or ""


@dataclass
class StreamChunk:
    content: str = ""
