from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from httpx import ReadTimeout
from ollama import ResponseError

from app.clients import OllamaClient, OllamaClientError


def test_client_uses_configured_host_timeout_and_chat_contract() -> None:
    provider = MagicMock()
    provider.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(content='{"category":"OTHER","description":"Draft"}')
    )
    messages = [{"role": "system", "content": "System"}]
    response_format = {"type": "object"}

    with patch(
        "app.clients.ollama_client.Client", return_value=provider
    ) as client_class:
        client = OllamaClient("http://ollama.test:11434", 12.5)
        content = client.chat("test-model", messages, response_format)

    client_class.assert_called_once_with(
        host="http://ollama.test:11434", timeout=12.5
    )
    provider.chat.assert_called_once_with(
        model="test-model",
        messages=messages,
        stream=False,
        format=response_format,
        options={"temperature": 0},
    )
    assert content == '{"category":"OTHER","description":"Draft"}'


@pytest.mark.parametrize(
    "provider_error",
    [
        ConnectionError("offline"),
        ResponseError("provider error", 500),
        ReadTimeout("timed out"),
    ],
)
def test_client_maps_provider_failures(provider_error: Exception) -> None:
    provider = MagicMock()
    provider.chat.side_effect = provider_error
    with patch("app.clients.ollama_client.Client", return_value=provider):
        client = OllamaClient("http://ollama.test:11434", 60)
    with pytest.raises(OllamaClientError, match="Ollama request failed"):
        client.chat("test-model", [], {"type": "object"})
