"""Custom exception classes for AI Handdrawn Toolkit."""
from enum import Enum


class ErrorCode(Enum):
    AUTH_ERROR = "AUTH_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_MODEL = "INVALID_MODEL"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED_IMAGE_INPUT = "UNSUPPORTED_IMAGE_INPUT"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    DOWNLOAD_ERROR = "DOWNLOAD_ERROR"
    IMAGE_DECODE_ERROR = "IMAGE_DECODE_ERROR"


class HanddrawnError(Exception):
    def __init__(self, code: ErrorCode, message: str, suggestion: str = ""):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"[{code.value}] {message}")
