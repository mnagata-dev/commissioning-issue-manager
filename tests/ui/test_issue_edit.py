"""Browser checks: run with pytest and Playwright/Chromium available.

API responses are intercepted; the production HTML, CSS and JS are used unchanged.
"""

from collections.abc import Generator
import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
PROJECT = {"id": 2, "name": "Commissioning", "hotel": {"id": 1, "name": "Hotel"}}
ISSUE = {
    "id": 101, "project": {"id": 2, "name": "Commissioning"},
    "status": "OPEN", "target_type": "ROOM", "room": {"id": 4, "room_number": "1203"},
    "target": None, "category": "LIGHTING", "description": "Original description",
}


@pytest.fixture(scope="module")
def browser() -> Generator:
    with playwright.sync_playwright() as driver:
        instance = driver.chromium.launch(headless=True)
        yield instance
        instance.close()


@pytest.fixture
def open_edit(browser) -> Generator:
    contexts = []
    errors = []

    def open_page(issue=None, failures=None, selected=True, query="?issue_id=101", detail=False):
        context = browser.new_context(viewport={"width": 390, "height": 844})
        contexts.append(context)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        calls = []
        failures = failures if failures is not None else {}
        if selected:
            # Initialize once so authentication redirects can really clear the selection.
            page.route("**/setup", lambda route: route.fulfill(body="<html></html>"))
            page.goto("http://cim.test/setup")
            page.evaluate("value => sessionStorage.setItem('cim.selectedProject', JSON.stringify(value))", PROJECT)

        def respond(route):
            path = urlparse(route.request.url).path
            method = route.request.method
            if path.startswith("/api/"):
                payload = route.request.post_data_json if route.request.post_data else None
                calls.append((method, path, payload))
                code = failures.get((method, path), 200)
                data = {"id": 101, "message": "Saved"}
                if code != 200:
                    data = {"error": {"code": "API_ERROR", "message": "Internal SECRET"}}
                elif path == "/api/auth/me":
                    data = {"display_name": "Engineer", "username": "engineer"}
                elif path == "/api/issues/101" and method == "GET":
                    data = ISSUE if issue is None else issue
                elif path.startswith("/api/hotels/"):
                    data = {"rooms": [{"id": 4, "room_number": "1203"}]}
                elif path == "/api/projects":
                    data = {"projects": [{**PROJECT, "id": 9, "hotel": {"id": 8, "name": "Other Hotel"}}]}
                route.fulfill(status=code, json=data)
            elif path in ("/", "/projects.html", "/issues.html"):
                route.fulfill(content_type="text/html", body="<h1>Destination</h1>")
            else:
                route.fulfill(path=str(FRONTEND / path.lstrip("/")))

        page.route("**/*", respond)
        page.goto("http://cim.test/" + ("issue.html" if detail else "issue-edit.html") + query)
        return page, calls

    yield open_page
    for context in contexts:
        context.close()
    assert not errors


def writes(calls: list) -> list:
    return [call for call in calls if call[0] in ("PUT", "PATCH")]


def test_detail_link_initial_values_and_cancel(open_edit) -> None:
    page, calls = open_edit(detail=True)
    page.locator("#edit-issue-link").click()
    page.wait_for_url("**/issue-edit.html?issue_id=101")
    expect(page.locator("#save-button")).to_be_enabled()
    for field, value in {"status": "OPEN", "target-type": "ROOM", "room": "4",
                         "category": "LIGHTING", "description": "Original description"}.items():
        expect(page.locator(f"#{field}")).to_have_value(value)
    expect(page.locator("#target-field")).to_be_hidden()
    assert page.locator("#room").evaluate("el => el.required")
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.fill("#description", "Unsaved edit")
    page.select_option("#status", "CLOSED")
    page.locator("#cancel-link").click()
    page.wait_for_url("**/issue.html?issue_id=101")
    assert writes(calls) == []


@pytest.mark.parametrize("status", ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"])
def test_save_separates_content_and_status_and_blocks_duplicates(open_edit, status) -> None:
    page, calls = open_edit()
    expect(page.locator("#save-button")).to_be_enabled()
    page.fill("#description", "Updated")
    page.select_option("#status", status)
    page.evaluate("""() => {
        const form = document.querySelector('#issue-edit-form');
        form.dispatchEvent(new Event('submit', {cancelable: true}));
        form.dispatchEvent(new Event('submit', {cancelable: true}));
    }""")
    page.wait_for_url("**/issue.html?issue_id=101")
    expected = [("PUT", "/api/issues/101", {
        "room_id": 4, "target_type": "ROOM", "target": None,
        "category": "LIGHTING", "description": "Updated",
    })]
    if status != "OPEN":
        expected.append(("PATCH", "/api/issues/101/status", {"status": status}))
    assert writes(calls) == expected


@pytest.mark.parametrize("initial_type", ["ROOM", "OTHER"])
def test_target_switch_sends_null_for_unused_field(open_edit, initial_type) -> None:
    issue = dict(ISSUE)
    if initial_type == "OTHER":
        issue.update(target_type="OTHER", room=None, target="Network")
    page, calls = open_edit(issue=issue)
    expect(page.locator("#save-button")).to_be_enabled()
    if initial_type == "ROOM":
        page.select_option("#target-type", "OTHER")
        page.fill("#target", " Lobby ")
        expect(page.locator("#room-field")).to_be_hidden()
        assert page.locator("#target").evaluate("el => el.required")
    else:
        expect(page.locator("#target")).to_have_value("Network")
        page.select_option("#target-type", "ROOM")
        page.select_option("#room", "4")
    page.locator("#save-button").click()
    page.wait_for_url("**/issue.html?issue_id=101")
    payload = writes(calls)[0][2]
    assert payload["room_id"] == (None if initial_type == "ROOM" else 4)
    assert payload["target"] == ("Lobby" if initial_type == "ROOM" else None)


@pytest.mark.parametrize("field", ["target-type", "category", "description", "room", "target"])
def test_validation_prevents_all_writes(open_edit, field) -> None:
    page, calls = open_edit()
    expect(page.locator("#save-button")).to_be_enabled()
    page.select_option("#status", "CLOSED")
    if field == "target":
        page.select_option("#target-type", "OTHER")
    if field in ("description", "target"):
        page.fill(f"#{field}", "   ")
    else:
        page.select_option(f"#{field}", "")
    page.locator("#save-button").click()
    expect(page.locator(f"#{field}-error")).to_be_visible()
    expect(page.locator(f"#{field}")).to_be_focused()
    assert writes(calls) == []


@pytest.mark.parametrize(("method", "path"), [
    ("GET", "/api/auth/me"), ("GET", "/api/issues/101"),
    ("GET", "/api/hotels/1/rooms"), ("PUT", "/api/issues/101"),
    ("PATCH", "/api/issues/101/status"),
])
def test_authentication_failure_redirects_and_clears_selection(open_edit, method, path) -> None:
    page, calls = open_edit(failures={(method, path): 401})
    if method != "GET":
        expect(page.locator("#save-button")).to_be_enabled()
        page.select_option("#status", "CLOSED")
        page.locator("#save-button").click()
    page.wait_for_url("http://cim.test/")
    assert page.evaluate("sessionStorage.getItem('cim.selectedProject')") is None


@pytest.mark.parametrize(("method", "path"), [
    ("GET", "/api/issues/101"), ("PUT", "/api/issues/101"),
    ("PATCH", "/api/issues/101/status"),
])
def test_missing_issue_redirects(open_edit, method, path) -> None:
    page, calls = open_edit(failures={(method, path): 404})
    if method != "GET":
        expect(page.locator("#save-button")).to_be_enabled()
        page.select_option("#status", "CLOSED")
        page.locator("#save-button").click()
    page.wait_for_url("**/issues.html")


@pytest.mark.parametrize("query", ["", "?issue_id=0", "?issue_id=invalid", "?issue_id=9007199254740992"])
def test_invalid_id(open_edit, query) -> None:
    page, calls = open_edit(query=query)
    page.wait_for_url("**/issues.html")
    assert calls == []


def test_missing_project(open_edit) -> None:
    page, calls = open_edit(selected=False)
    page.wait_for_url("**/projects.html")
    assert calls == []


@pytest.mark.parametrize("method", ["PUT", "PATCH"])
def test_failed_save_preserves_input_and_can_retry(open_edit, method) -> None:
    path = "/api/issues/101" + ("/status" if method == "PATCH" else "")
    failures = {(method, path): 500}
    page, calls = open_edit(failures=failures)
    expect(page.locator("#save-button")).to_be_enabled()
    page.fill("#description", "Keep my edits")
    page.select_option("#status", "CLOSED")
    page.locator("#save-button").click()
    expect(page.locator("#issue-error")).to_be_visible()
    expect(page.locator("#description")).to_have_value("Keep my edits")
    expect(page.locator("#save-button")).to_be_enabled()
    assert "SECRET" not in page.locator("body").inner_text()
    if method == "PATCH":
        expect(page.locator("#issue-error")).to_contain_text("内容は保存済み")
    else:
        assert [call[0] for call in writes(calls)] == ["PUT"]
    failures.clear()
    page.locator("#save-button").click()
    page.wait_for_url("**/issue.html?issue_id=101")


def test_direct_link_uses_issue_project_hotel_without_changing_selection(open_edit) -> None:
    page, calls = open_edit(issue={**ISSUE, "project": {"id": 9, "name": "Other Project"}})
    expect(page.locator("#save-button")).to_be_enabled()
    assert ("GET", "/api/hotels/8/rooms", None) in calls
    assert page.evaluate("JSON.parse(sessionStorage.getItem('cim.selectedProject')).id") == 2
