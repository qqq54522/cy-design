"""统一异常模型 - 所有业务模块共享的异常基类和通用子类。

各模块应从此处导入异常，禁止自行定义 AppError 子类。
如需模块专属异常，在此文件中追加并保持统一签名。
"""

from __future__ import annotations


class AppError(Exception):
    """应用统一异常基类，所有业务异常应继承此类。"""

    def __init__(
        self,
        message: str,
        *,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict:
        payload: dict = {"code": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload


# ── 通用异常 ──────────────────────────────────────────────


class NotFoundError(AppError):
    """资源不存在（404）"""

    def __init__(self, resource: str = "资源", resource_id: str = ""):
        label = f"{resource} {resource_id}" if resource_id else resource
        super().__init__(f"{label} 不存在", code="NOT_FOUND", status_code=404)


class ValidationError(AppError):
    """请求参数校验失败（422）"""

    def __init__(self, message: str = "参数校验失败", details: dict | None = None):
        super().__init__(
            message, code="VALIDATION_ERROR", status_code=422, details=details
        )


class StorageError(AppError):
    """存储操作异常（500）"""

    def __init__(self, message: str = "存储异常"):
        super().__init__(message, code="STORAGE_ERROR", status_code=500)


class RateLimitError(AppError):
    """请求频率超限（429）"""

    def __init__(self, message: str = "请求过于频繁，请稍后再试"):
        super().__init__(message, code="RATE_LIMIT", status_code=429)


# ── AI 模型相关 ───────────────────────────────────────────


class ModelUnavailableError(AppError):
    """AI 模型不可用（503）"""

    def __init__(self, message: str = "当前模型不可用，正在切换备选方案"):
        super().__init__(message, code="MODEL_UNAVAILABLE", status_code=503)


class GenerationError(AppError):
    """AI 生成失败（500）"""

    def __init__(self, message: str = "生成失败，请稍后重试"):
        super().__init__(message, code="GENERATION_FAILED", status_code=500)


class GenerationTimeoutError(AppError):
    """AI 生成超时（504）"""

    def __init__(self, message: str = "生成超时，请重试"):
        super().__init__(message, code="GENERATION_TIMEOUT", status_code=504)


class AnalysisError(AppError):
    """图像/内容分析失败（502）— 表情包模块"""

    def __init__(self, message: str = "图像分析失败"):
        super().__init__(message, code="ANALYSIS_ERROR", status_code=502)


# ── 数据源 / 外部服务 ────────────────────────────────────


class ExternalServiceError(AppError):
    """外部服务调用失败（502）"""

    def __init__(self, message: str = "外部服务调用失败"):
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", status_code=502)


class HotListFetchError(ExternalServiceError):
    """热搜数据获取失败（502）— 素材抓取模块"""

    def __init__(self, platform: str = ""):
        msg = f"获取 {platform} 热搜数据失败" if platform else "热搜数据获取失败"
        super().__init__(msg)
        self.code = "HOTLIST_FETCH_ERROR"


# ── 文件相关 ──────────────────────────────────────────────


class FileValidationError(ValidationError):
    """文件校验失败（422）— 表情包模块"""

    def __init__(self, message: str = "文件校验失败"):
        super().__init__(message)
        self.code = "FILE_VALIDATION_ERROR"
