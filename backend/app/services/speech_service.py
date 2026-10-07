"""Speech transcription application service."""

from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.clients import SpeechClient, SpeechClientError
from app.core.exceptions import SpeechRecognitionError, ValidationError
from app.schemas import SpeechTranscriptionResponse


class SpeechService:
    def __init__(self, speech_client: SpeechClient) -> None:
        self.speech_client = speech_client

    def transcribe_audio(self, audio: UploadFile) -> SpeechTranscriptionResponse:
        """Validate input and return usable transcription text only."""
        self._validate_audio(audio)
        try:
            text = self.speech_client.transcribe_audio(audio)
        except SpeechClientError as error:
            raise SpeechRecognitionError() from error

        if not isinstance(text, str):
            raise SpeechRecognitionError()

        text = text.strip()
        if not text:
            raise SpeechRecognitionError()

        return SpeechTranscriptionResponse(text=text)

    @staticmethod
    def _validate_audio(audio: UploadFile) -> None:
        if not isinstance(audio, StarletteUploadFile):
            raise ValidationError("Audio must be a non-empty readable file.")
        try:
            audio.file.seek(0)
            content = audio.file.read(1)
            audio.file.seek(0)
        except (OSError, ValueError) as error:
            raise ValidationError("Audio must be a non-empty readable file.") from error
        if not content:
            raise ValidationError("Audio must be a non-empty readable file.")
