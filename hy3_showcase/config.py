"""配置加载 — 从环境变量读取 API 参数。"""
import os


def load_config():
    api_key = os.environ.get("HY3_API_KEY", "")
    mock_flag = os.environ.get("HY3_MOCK", "").lower()
    return {
        "api_base": os.environ.get("HY3_API_BASE", "http://localhost:8000/v1"),
        "api_key": api_key,
        "model": os.environ.get("HY3_MODEL", "hy3"),
        "mock": mock_flag in ("1", "true", "yes") or not api_key,
    }
