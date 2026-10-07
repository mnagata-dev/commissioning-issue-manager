"""Browser checks for Issue Create voice input."""

from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
PROJECT = {"id": 2, "name": "Commissioning", "hotel": {"id": 1, "name": "Hotel"}}
SPEECH_ERROR_MESSAGE = (
    "音声の文字起こしに失敗しました。\n\n"
    "再度音声入力を行うか、Voice / Text Input にテキストを入力してください。"
)


@pytest.fixture(scope="module")
def browser() -> Generator:
    with playwright.sync_playwright() as driver:
        instance = driver.chromium.launch(headless=True)
        yield instance
        instance.close()


@pytest.fixture
def open_create(browser) -> Generator:
    contexts = []
    errors = []

    def open_page(*, microphone_error=False, speech_status=200):
        context = browser.new_context(viewport={"width": 390, "height": 844})
        contexts.append(context)
        context.add_init_script(
            """
            (() => {
              const microphoneError = MICROPHONE_ERROR;
              window.recordingTest = { trackStops: 0 };
              const track = { stop: () => { window.recordingTest.trackStops += 1; } };
              const stream = { getAudioTracks: () => [track] };
              Object.defineProperty(navigator, "mediaDevices", {
                configurable: true,
                value: {
                  getUserMedia: async (constraints) => {
                    window.recordingTest.constraints = constraints;
                    if (microphoneError) throw new Error("Microphone denied");
                    return stream;
                  },
                },
              });
              window.MediaRecorder = class {
                constructor() {
                  this.state = "inactive";
                  this.listeners = {};
                }
                addEventListener(name, listener) { this.listeners[name] = listener; }
                start() { this.state = "recording"; }
                stop() {
                  this.state = "inactive";
                  const data = new Blob(["recorded audio"], { type: "audio/webm" });
                  queueMicrotask(() => {
                    this.listeners.dataavailable({ data });
                    this.listeners.stop();
                  });
                }
              };
            })();
            """.replace("MICROPHONE_ERROR", "true" if microphone_error else "false"),
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        calls = []
        page.route("**/setup", lambda route: route.fulfill(body="<html></html>"))
        page.goto("http://cim.test/setup")
        page.evaluate(
            "value => sessionStorage.setItem('cim.selectedProject', JSON.stringify(value))",
            PROJECT,
        )

        def respond(route):
            path = urlparse(route.request.url).path
            if path.startswith("/api/"):
                calls.append(
                    {
                        "method": route.request.method,
                        "path": path,
                        "content_type": route.request.headers.get("content-type", ""),
                        "body": route.request.post_data_buffer,
                    }
                )
                if path == "/api/auth/me":
                    route.fulfill(json={"display_name": "Engineer", "username": "engineer"})
                elif path.startswith("/api/hotels/"):
                    route.fulfill(json={"rooms": []})
                elif path == "/api/speech/transcriptions":
                    if speech_status == 200:
                        route.fulfill(json={"text": "ロビーの照明が点滅している"})
                    else:
                        route.fulfill(
                            status=speech_status,
                            json={"error": {"code": "SPEECH_RECOGNITION_ERROR", "message": "Internal"}},
                        )
                else:
                    route.fulfill(json={})
            else:
                route.fulfill(path=str(FRONTEND / path.lstrip("/")))

        page.route("**/*", respond)
        page.goto("http://cim.test/issue-create.html")
        expect(page.locator("#voice-input-button")).to_be_enabled()
        return page, calls

    yield open_page
    for context in contexts:
        context.close()
    assert not errors


def test_voice_input_records_transcribes_and_keeps_ai_draft_manual(open_create) -> None:
    page, calls = open_create()
    page.select_option("#category", "NETWORK")
    page.fill("#description", "Existing description")

    page.locator("#voice-input-button").click()
    expect(page.locator("#voice-input-button")).to_be_hidden()
    expect(page.locator("#stop-recording-button")).to_be_enabled()
    assert page.evaluate("window.recordingTest.constraints") == {"audio": True}

    page.locator("#stop-recording-button").click()
    expect(page.locator("#input-text")).to_have_value("ロビーの照明が点滅している")
    expect(page.locator("#voice-input-button")).to_be_enabled()
    assert page.evaluate("window.recordingTest.trackStops") >= 1

    speech_calls = [call for call in calls if call["path"] == "/api/speech/transcriptions"]
    assert len(speech_calls) == 1
    assert speech_calls[0]["method"] == "POST"
    assert speech_calls[0]["content_type"].startswith("multipart/form-data; boundary=")
    assert b'name="audio"' in speech_calls[0]["body"]
    assert not any(call["path"] == "/api/ai/issue-draft" for call in calls)
    expect(page.locator("#category")).to_have_value("NETWORK")
    expect(page.locator("#description")).to_have_value("Existing description")


@pytest.mark.parametrize(
    ("microphone_error", "speech_status"),
    [(True, 200), (False, 500)],
)
def test_voice_input_failure_shows_speech_error_and_allows_retry(
    open_create, microphone_error, speech_status
) -> None:
    page, _ = open_create(microphone_error=microphone_error, speech_status=speech_status)
    page.locator("#voice-input-button").click()
    if not microphone_error:
        page.locator("#stop-recording-button").click()

    expect(page.locator("#issue-error")).to_have_text(SPEECH_ERROR_MESSAGE)
    expect(page.locator("#voice-input-button")).to_be_enabled()
    expect(page.locator("#stop-recording-button")).to_be_hidden()
