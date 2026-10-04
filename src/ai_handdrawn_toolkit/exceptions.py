"""统一防御性异常层级。"""

class ToolkitError(Exception):
    """项目根异常类"""

    pass


class StyleNotFoundError(ToolkitError):
    """未找到指定的风格预设"""

    pass


class ProviderApiError(ToolkitError):
    """云端渲染 API 异常"""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"Provider API Error [{status_code}]: {message}")


class VectorizationError(ToolkitError):
    """矢量化后处理异常"""

    pass
