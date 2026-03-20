"""shared.backend 共享层基础测试"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))

from backend.core.exceptions import AppError, NotFoundError, ValidationError
from backend.core.responses import success, error, paginated, from_app_error


class TestAppError:
    def test_default_error(self):
        err = AppError("something went wrong")
        assert err.message == "something went wrong"
        assert err.code == "INTERNAL_ERROR"
        assert err.status_code == 500
        assert err.details == {}

    def test_custom_error(self):
        err = AppError("bad input", code="BAD_INPUT", status_code=400, details={"field": "name"})
        assert err.code == "BAD_INPUT"
        assert err.status_code == 400
        assert err.details == {"field": "name"}

    def test_to_dict(self):
        err = AppError("test", code="TEST", status_code=400)
        d = err.to_dict()
        assert d["code"] == "TEST"
        assert d["message"] == "test"


class TestNotFoundError:
    def test_with_resource(self):
        err = NotFoundError("项目", "abc123")
        assert "abc123" in err.message
        assert err.status_code == 404
        assert err.code == "NOT_FOUND"


class TestValidationError:
    def test_default(self):
        err = ValidationError()
        assert err.status_code == 422
        assert err.code == "VALIDATION_ERROR"


class TestResponses:
    def test_success(self):
        resp = success(data={"id": "123"})
        assert resp["success"] is True
        assert resp["data"]["id"] == "123"

    def test_error_response(self):
        resp = error(code="NOT_FOUND", message="not found", status_code=404)
        assert resp["success"] is False
        assert resp["error"]["code"] == "NOT_FOUND"

    def test_from_app_error(self):
        err = NotFoundError("任务", "xyz")
        resp = from_app_error(err)
        assert resp["success"] is False
        assert resp["error"]["code"] == "NOT_FOUND"

    def test_paginated(self):
        resp = paginated(items=[1, 2, 3], total=10, page=1, page_size=3)
        assert resp["success"] is True
        assert resp["data"]["total"] == 10
        assert resp["data"]["total_pages"] == 4
        assert len(resp["data"]["items"]) == 3
