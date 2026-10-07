"""Speech transcription API routes."""

from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUserDependency, SpeechServiceDependency
from app.schemas import SpeechTranscriptionResponse

router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/transcriptions", response_model=SpeechTranscriptionResponse)
def transcribe_speech(
    current_user: CurrentUserDependency,
    speech_service: SpeechServiceDependency,
    audio: UploadFile = File(...),
) -> SpeechTranscriptionResponse:
    del current_user
    return speech_service.transcribe_audio(audio)
