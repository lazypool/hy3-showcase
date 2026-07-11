class Hy3Error(Exception):
    """Hy3 客户端基础异常"""


class ConnectionError(Hy3Error):
    """API 连接失败（网络 / 超时 / DNS）"""


class AuthenticationError(Hy3Error):
    """API 鉴权失败（Key 无效 / 过期）"""


class RateLimitError(Hy3Error):
    """请求被限流"""


class ConfigurationError(Hy3Error):
    """客户端配置错误（无效参数等）"""


class MockOnlyFeature(Hy3Error):
    """当前功能仅在真实 API 模式下可用"""
