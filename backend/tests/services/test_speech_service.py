"""Speech service tests without persistence dependencies."""

from io import BytesIO
from unittest.mock import Mock

from fastapi import UploadFile
import pytest

from app.clients import SpeechClient, SpeechClientError
from app.core.exceptions import SpeechRecognitionError, ValidationError
from app.services import SpeechService


@pytest.fixture
def speech_client() -> Mock:
    client = Mock(spec=SpeechClient)
    client.transcribe_audio.return_value = "ロビーの照明が点滅している"
    return client


def test_transcription_returns_only_text(speech_client: Mock) -> None:
    audio = UploadFile(file=BytesIO(b"audio"))
    audio.file.seek(2)
    response = SpeechService(speech_client).transcribe_audio(audio)
    assert response.model_dump() == {"text": "ロビーの照明が点滅している"}
    speech_client.transcribe_audio.assert_called_once_with(audio)
    assert audio.file.tell() == 0


def test_transcription_strips_surrounding_whitespace(speech_client: Mock) -> None:
    speech_client.transcribe_audio.return_value = " \n\tロビーの照明 が点滅している\t\n "
    response = SpeechService(speech_client).transcribe_audio(
        UploadFile(file=BytesIO(b"audio"))
    )
    assert response.text == "ロビーの照明 が点滅している"


@pytest.mark.parametrize("audio", [None, b"audio", UploadFile(file=BytesIO())])
def test_invalid_audio_does_not_call_client(speech_client: Mock, audio) -> None:
    with pytest.raises(ValidationError):
        SpeechService(speech_client).transcribe_audio(audio)
    speech_client.transcribe_audio.assert_not_called()


def test_closed_audio_does_not_call_client(speech_client: Mock) -> None:
    audio = UploadFile(file=BytesIO(b"audio"))
    audio.file.close()
    with pytest.raises(ValidationError):
        SpeechService(speech_client).transcribe_audio(audio)
    speech_client.transcribe_audio.assert_not_called()


@pytest.mark.parametrize("text", [None, 123, {}, [], "", " \n\t"])
def test_unusable_transcription_is_recognition_error(speech_client: Mock, text) -> None:
    speech_client.transcribe_audio.return_value = text
    with pytest.raises(SpeechRecognitionError):
        SpeechService(speech_client).transcribe_audio(UploadFile(file=BytesIO(b"audio")))


def test_client_failure_is_safe_application_error(speech_client: Mock) -> None:
    speech_client.transcribe_audio.side_effect = SpeechClientError("private details")
    with pytest.raises(SpeechRecognitionError) as error:
        SpeechService(speech_client).transcribe_audio(UploadFile(file=BytesIO(b"audio")))
    assert error.value.message == "Speech recognition failed."
