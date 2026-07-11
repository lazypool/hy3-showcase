import os


def load_config():
    return {
        "api_base": os.environ.get("HY3_API_BASE", "http://localhost:8000/v1"),
        "api_key": os.environ.get("HY3_API_KEY", ""),
        "model": os.environ.get("HY3_MODEL", "hy3"),
        "mock": os.environ.get("HY3_MOCK", "").lower() in ("1", "true", "yes")
                 or not os.environ.get("HY3_API_KEY"),
    }
