"""Tests for Frontend file delivery."""

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def make_client() -> TestClient:
    return TestClient(create_app(Settings(session_secret="test-only-session-secret")))


def test_login_page_is_delivered_and_excluded_from_openapi() -> None:
    with make_client() as client:
        response = client.get("/")
        openapi_paths = client.get("/openapi.json").json()["paths"]

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "CIM Login" in response.text
    assert 'id="login-form"' in response.text
    assert 'for="username"' in response.text
    assert 'for="password"' in response.text
    assert 'href="/css/style.css"' in response.text
    assert 'src="/js/login.js"' in response.text
    assert "/" not in openapi_paths


def test_project_page_is_delivered_and_excluded_from_openapi() -> None:
    with make_client() as client:
        response = client.get("/projects.html")
        openapi_paths = client.get("/openapi.json").json()["paths"]

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Project Selection" in response.text
    assert 'id="project-list"' in response.text
    assert 'id="logout-button"' in response.text
    assert 'href="/css/style.css"' in response.text
    assert 'src="/js/projects.js"' in response.text
    assert "/projects.html" not in openapi_paths


def test_issue_list_page_is_delivered_and_excluded_from_openapi() -> None:
    with make_client() as client:
        response = client.get("/issues.html")
        openapi_paths = client.get("/openapi.json").json()["paths"]

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Issue List" in response.text
    assert 'id="issue-search-form"' in response.text
    assert 'id="keyword"' in response.text
    assert 'id="status"' in response.text
    assert 'id="category"' in response.text
    assert 'id="target-type"' in response.text
    assert 'id="issue-list"' in response.text
    assert 'id="pagination"' in response.text
    assert 'id="logout-button"' in response.text
    assert 'id="change-project-button"' in response.text
    assert 'href="/css/style.css"' in response.text
    assert 'src="/js/issues.js"' in response.text
    assert "/issues.html" not in openapi_paths


def test_issue_detail_page_is_delivered_and_excluded_from_openapi() -> None:
    with make_client() as client:
        response = client.get("/issue.html")
        openapi_paths = client.get("/openapi.json").json()["paths"]

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Issue Detail" in response.text
    assert 'id="issue-content"' in response.text
    assert 'id="issue-status"' in response.text
    assert 'id="issue-target-type"' in response.text
    assert 'id="issue-room"' in response.text
    assert 'id="issue-target"' in response.text
    assert 'id="issue-category"' in response.text
    assert 'id="issue-description"' in response.text
    assert 'id="comment-list"' in response.text
    assert 'id="attachment-list"' in response.text
    assert 'id="edit-issue-link"' in response.text
    assert 'id="add-comment-button"' in response.text
    assert 'id="upload-attachment-button"' in response.text
    assert 'id="back-to-issues-link"' in response.text
    assert 'href="/css/style.css"' in response.text
    assert 'src="/js/issue.js"' in response.text
    assert "/issue.html" not in openapi_paths


def test_css_is_delivered() -> None:
    with make_client() as client:
        response = client.get("/css/style.css")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/css")
    assert response.content


def test_javascript_modules_are_delivered() -> None:
    with make_client() as client:
        responses = [
            client.get(f"/js/{filename}")
            for filename in (
                "api.js",
                "auth.js",
                "login.js",
                "projects.js",
                "issues.js",
                "issue.js",
            )
        ]

    for response in responses:
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]
        assert response.content


def test_unknown_resources_do_not_use_login_page_fallback() -> None:
    with make_client() as client:
        responses = [
            client.get("/css/missing.css"),
            client.get("/js/missing.js"),
            client.get("/api/missing"),
            client.get("/missing-page"),
        ]

    for response in responses:
        assert response.status_code == 404
        assert "CIM Login" not in response.text


def test_api_routes_still_resolve_as_json() -> None:
    with make_client() as client:
        responses = [
            client.get("/api/auth/me"),
            client.get("/api/projects"),
            client.get("/api/projects/1/issues"),
        ]

    for response in responses:
        assert response.status_code == 401
        assert response.headers["content-type"].startswith("application/json")
        assert response.json()["error"]["code"] == "AUTHENTICATION_ERROR"
