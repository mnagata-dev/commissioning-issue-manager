"""Local speech recognition through ffmpeg and whisper.cpp."""

from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from fastapi import UploadFile


class SpeechClientError(Exception):
    """Raised when local audio conversion or recognition fails."""


class SpeechClient:
    def __init__(self, executable: str | None, model: str | None) -> None:
        self.executable = executable
        self.model = model

    def transcribe_audio(self, audio: UploadFile) -> str:
        """Transcribe audio using temporary files, removed on every exit path."""
        if not self.executable or not self.model:
            raise SpeechClientError("Speech recognition is not configured.")

        try:
            with TemporaryDirectory() as directory:
                input_path = Path(directory) / "input"
                wav_path = Path(directory) / "audio.wav"
                output_path = Path(directory) / "transcription"
                audio.file.seek(0)
                with input_path.open("wb") as input_file:
                    shutil.copyfileobj(audio.file, input_file)

                subprocess.run(
                    [
                        "ffmpeg", "-nostdin", "-y", "-i", str(input_path),
                        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                        str(wav_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
                subprocess.run(
                    [
                        self.executable, "-m", self.model, "-f", str(wav_path),
                        "-l", "ja", "-otxt", "-of", str(output_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                )
                return output_path.with_suffix(".txt").read_text(encoding="utf-8")
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            raise SpeechClientError("Local speech recognition failed.") from error
