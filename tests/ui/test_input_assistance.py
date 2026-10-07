"""Input Assistance browser checks using production pages and intercepted APIs."""

from collections.abc import Generator
import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
PROJECT = {"id": 2, "name": "Commissioning", "hotel": {"id": 1, "name": "Hotel"}}
OTHER_PROJECT = {"id": 9, "name": "Other Project", "hotel": {"id": 8, "name": "Other Hotel"}}
KEY = "cim.inputAssistance.2"
OTHER_KEY = "cim.inputAssistance.9"
SAVED = {"target_type": "ROOM", "room_id": 4, "category": "LIGHTING", "target_history": ["Lobby"]}


@pytest.fixture(scope="module")
def browser() -> Generator:
    with playwright.sync_playwright() as driver:
        instance = driver.chromium.launch(headless=True)
        yield instance
        instance.close()


@pytest.fixture
def open_page(browser) -> Generator:
    contexts = []
    errors = []

    def open_browser(*, stored=None, storage_error=None, create_status=201,
                     create_response=None, edit=False, project=PROJECT):
        context = browser.new_context(viewport={"width": 390, "height": 844})
        contexts.append(context)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        calls = []
        page.route("**/setup", lambda route: route.fulfill(body="<html></html>"))
        page.goto("http://cim.test/setup")
        page.evaluate(
            "value => sessionStorage.setItem('cim.selectedProject', JSON.stringify(value))", project,
        )
        page.evaluate(
            "values => { for (const [key, value] of Object.entries(values)) localStorage.setItem(key, value); }",
            stored or {},
        )
        if storage_error == "access":
            context.add_init_script("""Object.defineProperty(window, 'localStorage', {
                get() { throw new Error('Storage unavailable'); }
            });""")
        elif storage_error:
            context.add_init_script("""(() => {
                const method = METHOD;
                const original = Storage.prototype[method];
                Storage.prototype[method] = function(...args) {
                    if (this === window.localStorage) throw new Error('Storage unavailable');
                    return original.apply(this, args);
                };
            })();""".replace("METHOD", json.dumps(storage_error)))

        def respond(route):
            path = urlparse(route.request.url).path
            method = route.request.method
            if path.startswith("/api/"):
                payload = route.request.post_data_json if route.request.post_data else None
                calls.append((method, path, payload))
                status = 200
                data = {"id": 101}
                if path == "/api/auth/me":
                    data = {"display_name": "Engineer", "username": "engineer"}
                elif path.startswith("/api/hotels/"):
                    room_id = 4 if path == "/api/hotels/1/rooms" else 8
                    data = {"rooms": [{"id": room_id, "room_number": "1203"}]}
                elif path == "/api/issues/101" and method == "GET":
                    data = {
                        "id": 101, "project": {"id": 2, "name": "Commissioning"},
                        "status": "OPEN", "target_type": "ROOM", "room": {"id": 4},
                        "target": None, "category": "LIGHTING", "description": "Original",
                    }
                elif method == "POST" and path.endswith("/issues"):
                    status = create_status
                    data = {"id": 101} if create_response is None else create_response
                    if status >= 400:
                        data = {"error": {"code": "API_ERROR", "message": "Create failed"}}
                elif path == "/api/ai/issue-draft":
                    data = {"category": "NETWORK", "description": "Generated description"}
                route.fulfill(status=status, json=data)
            elif path in ("/issue.html", "/issues.html"):
                route.fulfill(content_type="text/html", body="<h1>Destination</h1>")
            else:
                route.fulfill(path=str(FRONTEND / path.lstrip("/")))

        page.route("**/*", respond)
        page.goto("http://cim.test/" + ("issue-edit.html?issue_id=101" if edit else "issue-create.html"))
        expect(page.locator("#save-button" if edit else "#create-button")).to_be_enabled()
        return page, calls

    yield open_browser
    for context in contexts:
        context.close()
    assert not errors


def snapshot(page) -> dict:
    return page.evaluate("Object.fromEntries(Object.entries(localStorage))")


def fill_create(page, target_type="ROOM", target="Lobby") -> None:
    page.select_option("#target-type", target_type)
    if target_type == "ROOM":
        page.select_option("#room", "4")
    else:
        page.fill("#target", target)
    page.select_option("#category", "NETWORK")
    page.fill("#description", "New description")


def submit_create(page) -> None:
    page.locator("#create-button").click()
    page.wait_for_url("**/issue.html?issue_id=101")


def test_create_saves_used_values_and_reopening_restores_them(open_page) -> None:
    page, _ = open_page()
    fill_create(page)
    assert snapshot(page) == {}
    submit_create(page)
    saved = json.loads(snapshot(page)[KEY])
    assert saved == {"target_type": "ROOM", "room_id": 4, "category": "NETWORK", "target_history": []}
    page.goto("http://cim.test/issue-create.html")
    expect(page.locator("#create-button")).to_be_enabled()
    for field, value in {"target-type": "ROOM", "room": "4", "category": "NETWORK"}.items():
        expect(page.locator(f"#{field}")).to_have_value(value)
    expect(page.locator("#description")).to_have_value("")


def test_project_isolation_for_restore_history_and_save(open_page) -> None:
    other_saved = {"target_type": "OTHER", "room_id": None, "category": "SHADE", "target_history": ["Other lobby"]}
    stored = {KEY: json.dumps(SAVED), OTHER_KEY: json.dumps(other_saved)}
    page, _ = open_page(stored=stored, project=OTHER_PROJECT)
    expect(page.locator("#target-type")).to_have_value("OTHER")
    expect(page.locator("#category")).to_have_value("SHADE")
    assert page.locator("#target-history option").all_text_contents() == ["履歴から選択（任意）", "Other lobby"]
    expect(page.locator("#target")).to_have_value("")
    page.fill("#target", "Other new target")
    page.fill("#description", "Other description")
    submit_create(page)
    assert snapshot(page)[KEY] == stored[KEY]
    assert json.loads(snapshot(page)[OTHER_KEY]) == {**other_saved, "target_history": ["Other lobby", "Other new target"]}
    page.evaluate("value => sessionStorage.setItem('cim.selectedProject', JSON.stringify(value))", PROJECT)
    page.goto("http://cim.test/issue-create.html")
    expect(page.locator("#create-button")).to_be_enabled()
    expect(page.locator("#target-type")).to_have_value("ROOM")
    expect(page.locator("#room")).to_have_value("4")
    expect(page.locator("#category")).to_have_value("LIGHTING")
    page.select_option("#target-type", "OTHER")
    assert page.locator("#target-history option").all_text_contents() == ["履歴から選択（任意）", "Lobby"]


@pytest.mark.parametrize("stored", [
    {}, {KEY: "not JSON"}, {KEY: "null"}, {KEY: "[]"}, {KEY: '"ROOM"'},
    {KEY: json.dumps({"target_type": "AREA", "room_id": "4", "category": "INVALID", "target_history": "Lobby"})},
])
def test_missing_malformed_or_invalid_saved_values_use_normal_defaults(open_page, stored) -> None:
    page, _ = open_page(stored=stored)
    for field in ("target-type", "room", "category", "target"):
        expect(page.locator(f"#{field}")).to_have_value("")
    fill_create(page)
    submit_create(page)


@pytest.mark.parametrize("room_id", [8, 999, None, -1])
def test_unavailable_room_is_not_restored_but_valid_fields_are(open_page, room_id) -> None:
    page, _ = open_page(stored={KEY: json.dumps({**SAVED, "room_id": room_id})})
    expect(page.locator("#target-type")).to_have_value("ROOM")
    expect(page.locator("#category")).to_have_value("LIGHTING")
    expect(page.locator("#room")).to_have_value("")


@pytest.mark.parametrize("mode", ["candidate", "free", "edited_candidate"])
def test_other_history_can_be_selected_or_bypassed_and_saved(open_page, mode) -> None:
    page, calls = open_page(stored={KEY: json.dumps(SAVED)})
    expect(page.locator("#target-history-field")).to_be_hidden()
    page.select_option("#target-type", "OTHER")
    expect(page.locator("#target-history-field")).to_be_visible()
    expect(page.locator("#target")).to_have_value("")
    if mode != "free":
        page.select_option("#target-history", "Lobby")
        expect(page.locator("#target")).to_have_value("Lobby")
    target = "Lobby" if mode == "candidate" else "自由入力の対象"
    if mode != "candidate":
        page.fill("#target", f" {target} ")
    page.fill("#description", "Other description")
    submit_create(page)
    saved = json.loads(snapshot(page)[KEY])
    assert saved == {"target_type": "OTHER", "room_id": None, "category": "LIGHTING", "target_history": ["Lobby", target]}
    create = next(call for call in calls if call[0] == "POST")
    assert create[2]["target"] == target
    assert create[2]["room_id"] is None
    assert not any(call[1] == "/api/ai/issue-draft" for call in calls)


def test_room_create_preserves_other_history_without_adding_to_it(open_page) -> None:
    page, _ = open_page(stored={KEY: json.dumps(SAVED)})
    fill_create(page)
    submit_create(page)
    assert json.loads(snapshot(page)[KEY])["target_history"] == ["Lobby"]


@pytest.mark.parametrize(("create_status", "create_response"), [(400, None), (500, None), (201, {})])
def test_failed_create_does_not_update_previous_values_or_history(open_page, create_status, create_response) -> None:
    stored = {KEY: json.dumps(SAVED)}
    page, _ = open_page(stored=stored, create_status=create_status, create_response=create_response)
    fill_create(page, "OTHER", "Not saved")
    page.locator("#create-button").click()
    expect(page.locator("#issue-error")).to_be_visible()
    expect(page.locator("#create-button")).to_be_enabled()
    assert snapshot(page) == stored


def test_validation_draft_and_cancel_do_not_save_assistance(open_page) -> None:
    stored = {KEY: json.dumps(SAVED)}
    page, calls = open_page(stored=stored)
    page.locator("#create-button").click()
    expect(page.locator("#description-error")).to_be_visible()
    assert not any(call[0] == "POST" for call in calls)
    page.fill("#input-text", "Draft input")
    page.locator("#generate-draft-button").click()
    expect(page.locator("#draft-message")).to_be_visible()
    expect(page.locator("#target-type")).to_have_value("ROOM")
    expect(page.locator("#room")).to_have_value("4")
    assert snapshot(page) == stored
    page.locator("#cancel-link").click()
    page.wait_for_url("**/issues.html")
    assert snapshot(page) == stored


@pytest.mark.parametrize("storage_error", ["access", "getItem", "setItem"])
def test_storage_failures_do_not_prevent_normal_create(open_page, storage_error) -> None:
    page, calls = open_page(storage_error=storage_error)
    fill_create(page, "OTHER", "New target")
    submit_create(page)
    assert len([call for call in calls if call[0] == "POST"]) == 1


def test_edit_keeps_issue_values_and_does_not_change_assistance(open_page) -> None:
    stored = {KEY: json.dumps({"target_type": "OTHER", "room_id": None, "category": "NETWORK", "target_history": ["Saved target"]})}
    page, calls = open_page(stored=stored, edit=True)
    for field, value in {"target-type": "ROOM", "room": "4", "category": "LIGHTING", "description": "Original"}.items():
        expect(page.locator(f"#{field}")).to_have_value(value)
    page.select_option("#target-type", "OTHER")
    page.fill("#target", "Updated target")
    page.select_option("#category", "SHADE")
    page.locator("#save-button").click()
    page.wait_for_url("**/issue.html?issue_id=101")
    assert any(call[0] == "PUT" and call[2]["target"] == "Updated target" for call in calls)
    assert snapshot(page) == stored
