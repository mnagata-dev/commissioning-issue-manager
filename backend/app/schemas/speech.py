"""Speech transcription response schema."""

from pydantic import BaseModel, ConfigDict


class SpeechTranscriptionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
