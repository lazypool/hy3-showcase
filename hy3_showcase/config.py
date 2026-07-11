import os

from .errors import ConfigurationError

_DEFAULTS = {
    "api_base": "http://localhost:8000/v1",
    "model": "hy3",
}

_REQUIRED_KEYS = {"api_base", "api_key", "model", "mock"}


def load_config() -> dict:
    api_key = os.environ.get("HY3_API_KEY", "")
    mock_env = os.environ.get("HY3_MOCK", "").lower()

    config = {
        "api_base": os.environ.get("HY3_API_BASE", _DEFAULTS["api_base"]),
        "api_key": api_key,
        "model": os.environ.get("HY3_MODEL", _DEFAULTS["model"]),
        "mock": mock_env in ("1", "true", "yes") or not api_key,
    }

    if not config["api_base"]:
        raise ConfigurationError("HY3_API_BASE 不能为空")

    return config
