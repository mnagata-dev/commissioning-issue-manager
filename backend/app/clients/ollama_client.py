"""Ollama provider integration."""

import json
from collections.abc import Mapping, Sequence
from typing import Any

import httpx
from ollama import Client, RequestError, ResponseError
from pydantic import ValidationError as PydanticValidationError


class OllamaClientError(Exception):
    """Raised when Ollama communication or extraction fails."""


class OllamaClient:
    def __init__(self, host: str, timeout_seconds: float) -> None:
        self._client = Client(host=host, timeout=timeout_seconds)

    def chat(
        self,
        model: str,
        messages: Sequence[Mapping[str, str]],
        response_format: dict[str, Any],
    ) -> str:
        try:
            response = self._client.chat(
                model=model,
                messages=messages,
                stream=False,
                format=response_format,
                options={"temperature": 0},
            )
            return response.message.content
        except (
            ConnectionError,
            RequestError,
            ResponseError,
            httpx.TimeoutException,
            json.JSONDecodeError,
            PydanticValidationError,
        ) as error:
            raise OllamaClientError("Ollama request failed.") from error
