"""统一 API 响应格式 - 所有模块和平台 API 的标准响应结构。"""

from __future__ import annotations

from typing import Any

from .exceptions import AppError


def success(*, data: Any = None, message: str = "ok") -> dict:
    """标准成功响应"""
    return {"success": True, "message": message, "data": data}


def error(
    *,
    code: str = "INTERNAL_ERROR",
    message: str = "服务异常",
    status_code: int = 500,
    details: dict | None = None,
) -> dict:
    """标准错误响应"""
    payload: dict = {
        "success": False,
        "error": {"code": code, "message": message},
    }
    if details:
        payload["error"]["details"] = details
    return payload


def from_app_error(exc: AppError) -> dict:
    """从 AppError 构建标准错误响应"""
    return error(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


def paginated(
    *,
    items: list,
    total: int,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """标准分页响应"""
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }
