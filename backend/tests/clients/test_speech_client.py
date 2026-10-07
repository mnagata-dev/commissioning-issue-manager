"""Local process boundary tests; no installed tools or models are required."""

from io import BytesIO
from pathlib import Path
import subprocess
from unittest.mock import Mock

from fastapi import UploadFile
import pytest

from app.clients import SpeechClient, SpeechClientError


@pytest.mark.parametrize(
    "failure",
    [None, "ffmpeg", "whisper", "missing_text", "invalid_encoding", "copy"],
)
def test_process_interaction_and_cleanup(monkeypatch, failure: str | None) -> None:
    directories: list[Path] = []
    commands: list[list[str]] = []

    def run(command: list[str], **kwargs) -> None:
        commands.append(command)
        assert kwargs == {
            "check": True, "stdout": subprocess.DEVNULL, "stderr": subprocess.PIPE
        }
        if command[0] == "ffmpeg":
            input_path = Path(command[command.index("-i") + 1])
            directories.append(input_path.parent)
            assert input_path.read_bytes() == b"audio"
            assert command == [
                "ffmpeg", "-nostdin", "-y", "-i", str(input_path),
                "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
                str(input_path.parent / "audio.wav"),
            ]
            if failure == "ffmpeg":
                raise subprocess.CalledProcessError(1, command, stderr=b"private")
            Path(command[-1]).write_bytes(b"converted")
        else:
            output = Path(command[command.index("-of") + 1])
            assert command == [
                "/local path/whisper-cli", "-m", "/model path/model.bin",
                "-f", str(output.parent / "audio.wav"),
                "-l", "ja", "-otxt", "-of", str(output),
            ]
            assert (output.parent / "audio.wav").read_bytes() == b"converted"
            if failure == "whisper":
                raise subprocess.CalledProcessError(1, command)
            if failure != "missing_text":
                output.with_suffix(".txt").write_bytes(
                    b"\xff" if failure == "invalid_encoding" else "認識結果\n".encode()
                )

    monkeypatch.setattr("app.clients.speech_client.subprocess.run", run)
    if failure == "copy":
        def fail_copy(source, destination) -> None:
            directories.append(Path(destination.name).parent)
            raise OSError("copy failed")
        monkeypatch.setattr("app.clients.speech_client.shutil.copyfileobj", fail_copy)
    client = SpeechClient("/local path/whisper-cli", "/model path/model.bin")
    audio = UploadFile(filename="../../untrusted", file=BytesIO(b"audio"))
    if failure:
        with pytest.raises(SpeechClientError):
            client.transcribe_audio(audio)
    else:
        assert client.transcribe_audio(audio) == "認識結果\n"
    assert directories
    assert all(not directory.exists() for directory in directories)
    assert not audio.file.closed
    if failure == "ffmpeg":
        assert len(commands) == 1


@pytest.mark.parametrize("stage", [1, 2])
def test_missing_executable_cleans_up(monkeypatch, stage: int) -> None:
    directories = []

    def run(command, **kwargs) -> None:
        if command[0] == "ffmpeg":
            directories.append(Path(command[-1]).parent)
        if len(calls) + 1 == stage:
            raise FileNotFoundError("missing executable")
        calls.append(command)

    calls = []
    monkeypatch.setattr("app.clients.speech_client.subprocess.run", run)
    with pytest.raises(SpeechClientError):
        SpeechClient("whisper", "model").transcribe_audio(
            UploadFile(file=BytesIO(b"audio"))
        )
    assert all(not directory.exists() for directory in directories)


@pytest.mark.parametrize("executable,model", [(None, "model"), ("cli", None), ("", "")])
def test_missing_configuration_does_not_launch_process(monkeypatch, executable, model):
    run = Mock()
    monkeypatch.setattr("app.clients.speech_client.subprocess.run", run)
    with pytest.raises(SpeechClientError):
        SpeechClient(executable, model).transcribe_audio(UploadFile(file=BytesIO(b"audio")))
    run.assert_not_called()
