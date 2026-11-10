import json
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from app.api.exception_handlers import (
    register_exception_handlers,
    validation_exception_handler,
)
from app.api.rest.constants.http_codes import HttpCode
from app.api.sanitizers import sanitize_validation_errors


class TestSanitizeValidationErrors:
    def test_strips_input_field_from_error_dicts(self) -> None:
        raw_errors = [
            {"loc": ("body", "password"), "msg": "too short", "type": "string_too_short", "input": "secret123"},
            {"loc": ("body", "email"), "msg": "invalid format", "type": "value_error", "input": "bad@"},
        ]

        cleaned = sanitize_validation_errors(raw_errors)

        assert len(cleaned) == 2
        assert "input" not in cleaned[0]
        assert "input" not in cleaned[1]
        assert cleaned[0]["loc"] == ("body", "password")
        assert cleaned[0]["msg"] == "too short"
        assert cleaned[1]["loc"] == ("body", "email")


    def test_empty_list_returns_empty(self) -> None:
        assert sanitize_validation_errors([]) == []


class TestValidationExceptionHandler:
    @pytest.mark.anyio
    async def test_returns_422_with_sanitized_detail(self) -> None:
        mock_request = MagicMock(spec=Request)
        exc = RequestValidationError(
            errors=[
                {"loc": ("body", "password"), "msg": "too short", "type": "value_error", "input": "mypassword"},
            ]
        )

        response = await validation_exception_handler(mock_request, exc)

        assert response.status_code == HttpCode._422
        body = json.loads(response.body.decode("utf-8"))
        assert "detail" in body
        assert len(body["detail"]) == 1
        assert "input" not in body["detail"][0]
        assert "mypassword" not in response.body.decode("utf-8")


    def test_register_exception_handlers(self) -> None:
        app = FastAPI()
        register_exception_handlers(app)
        assert RequestValidationError in app.exception_handlers
        assert app.exception_handlers[RequestValidationError] is validation_exception_handler
