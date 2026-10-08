"""CLI commands, safe input/output, exit codes and terminal integration."""

import getpass
import os
import select
import subprocess
import time
import warnings
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from app.cli import __main__ as cli
from app.db import session as session_module
from app.schemas.administration import CreateHotelRequest, CreateRoomTypeRequest


@pytest.fixture
def runtime(monkeypatch, administration_engine):
    sessions = []

    def create_session():
        session = Session(administration_engine, expire_on_commit=False)
        session.close = MagicMock(wraps=session.close)
        session.commit = MagicMock(wraps=session.commit)
        session.rollback = MagicMock(wraps=session.rollback)
        sessions.append(session)
        return session

    passwords = MagicMock(return_value="admin-pass")
    monkeypatch.setattr(session_module, "SessionLocal", create_session)
    monkeypatch.setattr(cli.getpass, "getpass", passwords)
    return sessions, passwords


@pytest.mark.parametrize(
    "target, create_fields, update_fields",
    [
        ("hotel", ["--name", "New"], ["--name", "Changed"]),
        ("project", ["--hotel-id", "{hotel}", "--name", "New"], ["--name", "Changed"]),
        (
            "room-type",
            ["--hotel-id", "{hotel}", "--name", "New"],
            ["--name", "Changed"],
        ),
        (
            "room",
            [
                "--hotel-id",
                "{hotel}",
                "--room-type-id",
                "{type}",
                "--room-number",
                "101",
            ],
            ["--display-name", "Changed"],
        ),
        (
            "user",
            ["--username", "new", "--display-name", "New", "--role", "ENGINEER"],
            ["--display-name", "Changed"],
        ),
    ],
)
def test_create_update_all_commands(
    runtime, service, admin_id, target, create_fields, update_fields, capsys
) -> None:
    hotel = service.create_hotel(
        "admin", "admin-pass", CreateHotelRequest(name="Parent")
    )
    room_type = service.create_room_type(
        "admin", "admin-pass", CreateRoomTypeRequest(hotel_id=hotel.id, name="Twin")
    )
    replacements = {"{hotel}": str(hotel.id), "{type}": str(room_type.id)}
    create_fields = [replacements.get(value, value) for value in create_fields]
    sessions, passwords = runtime
    assert (
        cli.main([target, "create", "--admin-username", "admin", *create_fields]) == 0
    )
    output = capsys.readouterr()
    entity_id = output.out.split()[1].rstrip(":")
    assert passwords.call_count == (2 if target == "user" else 1)
    assert (
        cli.main(
            [target, "update", entity_id, "--admin-username", "admin", *update_fields]
        )
        == 0
    )
    assert cli.main([target, "update", entity_id, "--admin-username", "admin"]) == 0
    for session in sessions:
        session.commit.assert_called_once()
        session.close.assert_called_once()
    output = capsys.readouterr()
    assert not output.err and "admin-pass" not in output.out


def test_bootstrap_password_change_and_guard(
    runtime, administration_engine, capsys
) -> None:
    from app.core.security import verify_password
    from app.models import User

    sessions, passwords = runtime
    assert (
        cli.main(
            ["user", "bootstrap-admin", "--username", "admin", "--display-name", "A"]
        )
        == 0
    )
    passwords.assert_called_once_with("New User password: ")
    admin_id = capsys.readouterr().out.split()[1].rstrip(":")
    assert (
        cli.main(
            ["user", "bootstrap-admin", "--username", "other", "--display-name", "O"]
        )
        == 1
    )
    assert "Bootstrap" in capsys.readouterr().err
    assert (
        cli.main(
            [
                "user",
                "update",
                admin_id,
                "--admin-username",
                "admin",
                "--role",
                "ENGINEER",
            ]
        )
        == 1
    )
    assert "Administrator must remain" in capsys.readouterr().err
    passwords.reset_mock()
    passwords.side_effect = ["admin-pass", "new-secret"]
    assert (
        cli.main(
            ["user", "update", admin_id, "--admin-username", "admin", "--set-password"]
        )
        == 0
    )
    assert [call.args[0] for call in passwords.call_args_list] == [
        "Administrator password: ",
        "New User password: ",
    ]
    with Session(administration_engine) as check:
        assert verify_password(
            "new-secret", check.get(User, int(admin_id)).password_hash
        )
    assert "new-secret" not in capsys.readouterr().out
    for session in sessions:
        session.close.assert_called_once()


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["hotel"],
        ["hotel", "delete"],
        ["csv"],
        ["hotel", "create", "--name", "H"],
        ["hotel", "create", "--admin-username", "admin"],
        ["hotel", "update", "invalid", "--admin-username", "admin"],
        [
            "project",
            "create",
            "--admin-username",
            "admin",
            "--name",
            "P",
            "--hotel-id",
            "x",
        ],
        [
            "user",
            "create",
            "--admin-username",
            "admin",
            "--username",
            "u",
            "--display-name",
            "U",
            "--role",
            "UNKNOWN",
        ],
        ["project", "update", "1", "--admin-username", "admin", "--hotel-id", "2"],
        ["room-type", "update", "1", "--admin-username", "admin", "--hotel-id", "2"],
        ["room", "update", "1", "--admin-username", "admin", "--hotel-id", "2"],
        [
            "user",
            "bootstrap-admin",
            "--username",
            "u",
            "--display-name",
            "U",
            "--role",
            "ENGINEER",
        ],
        [
            "hotel",
            "create",
            "--admin-username",
            "admin",
            "--name",
            "H",
            "--password",
            "misplaced-secret",
        ],
    ],
)
def test_usage_errors(runtime, argv, capsys) -> None:
    sessions, passwords = runtime
    with pytest.raises(SystemExit) as error:
        cli.main(argv)
    assert error.value.code == 2 and sessions == []
    passwords.assert_not_called()
    assert "misplaced-secret" not in capsys.readouterr().err


@pytest.mark.parametrize(
    "argv", [["--help"], ["user", "--help"], ["room", "update", "--help"]]
)
def test_help_without_input_or_db(runtime, argv) -> None:
    sessions, passwords = runtime
    with pytest.raises(SystemExit) as error:
        cli.main(argv)
    assert error.value.code == 0 and sessions == []
    passwords.assert_not_called()


@pytest.mark.parametrize(
    "failure", [EOFError(), KeyboardInterrupt(), getpass.GetPassWarning()]
)
def test_hidden_input_failure(runtime, failure, capsys) -> None:
    sessions, passwords = runtime
    passwords.side_effect = failure
    assert (
        cli.main(["hotel", "create", "--admin-username", "admin", "--name", "H"]) == 1
    )
    assert sessions == [] and "interrupted" in capsys.readouterr().err


def test_warning_aborts_before_fallback(runtime, monkeypatch) -> None:
    fallback = MagicMock()

    def unavailable(prompt):
        warnings.warn("Cannot hide input", getpass.GetPassWarning)
        return fallback()

    monkeypatch.setattr(cli.getpass, "getpass", unavailable)
    assert (
        cli.main(["hotel", "create", "--admin-username", "admin", "--name", "H"]) == 1
    )
    fallback.assert_not_called()
    assert runtime[0] == []


@pytest.mark.parametrize(
    "username, password",
    [("missing", "pw"), ("admin", "wrong"), ("admin", "admin-pass")],
)
def test_authentication_or_db_failure_safe_output(
    runtime, admin_id, username, password, monkeypatch, capsys
) -> None:
    sessions, passwords = runtime
    passwords.return_value = password
    original = session_module.SessionLocal
    if password == "admin-pass":

        def failing_session():
            session = original()
            session.commit.side_effect = RuntimeError(
                "SQL password=private sqlite:///secret.db traceback"
            )
            return session

        monkeypatch.setattr(session_module, "SessionLocal", failing_session)
    assert (
        cli.main(["hotel", "create", "--admin-username", username, "--name", "H"]) == 1
    )
    sessions[0].rollback.assert_called_once()
    sessions[0].close.assert_called_once()
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == (
        "Administration command failed.\n"
        if password == "admin-pass"
        else "Authentication failed.\n"
    )


def test_module_help_subprocess() -> None:
    environment = os.environ.copy()
    environment["UV_CACHE_DIR"] = "/tmp/cim-uv-cache"
    result = subprocess.run(
        ["uv", "run", "python", "-m", "app.cli", "--help"],
        capture_output=True,
        text=True,
        env=environment,
        timeout=20,
    )
    assert result.returncode == 0 and "room-type" in result.stdout


@pytest.mark.skipif(os.name != "posix", reason="POSIX terminal integration")
def test_module_hidden_terminal(admin_id, administration_engine) -> None:
    import fcntl
    import pty
    import termios

    master, slave = pty.openpty()

    def controlling_terminal():
        os.setsid()
        fcntl.ioctl(0, termios.TIOCSCTTY, 0)

    environment = os.environ.copy()
    environment["CIM_DATABASE_URL"] = str(administration_engine.url)
    environment["UV_CACHE_DIR"] = "/tmp/cim-uv-cache"
    process = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            "-m",
            "app.cli",
            "hotel",
            "create",
            "--admin-username",
            "admin",
            "--name",
            "Terminal Hotel",
        ],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        env=environment,
        preexec_fn=controlling_terminal,
    )
    os.close(slave)
    output = b""
    password_sent = False
    deadline = time.monotonic() + 20
    try:
        while time.monotonic() < deadline:
            readable, _, _ = select.select([master], [], [], 0.1)
            if readable:
                try:
                    data = os.read(master, 4096)
                except OSError:
                    break
                if not data:
                    break
                output += data
                if b"Administrator password:" in output and not password_sent:
                    os.write(master, b"admin-pass\n")
                    password_sent = True
        assert process.wait(timeout=2) == 0, output.decode()
        assert password_sent and b"succeeded" in output
        assert b"admin-pass" not in output
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        os.close(master)


def test_engineer_rejected_and_validation_exit(
    runtime, service, admin_id, capsys
) -> None:
    from app.schemas.administration import CreateUserRequest

    service.create_user(
        "admin",
        "admin-pass",
        CreateUserRequest(
            username="engineer", display_name="E", password="pw", role="ENGINEER"
        ),
    )
    sessions, passwords = runtime
    passwords.return_value = "pw"
    assert (
        cli.main(["hotel", "create", "--admin-username", "engineer", "--name", "H"])
        == 1
    )
    assert capsys.readouterr().err == "Access is not permitted.\n"
    passwords.return_value = "admin-pass"
    assert (
        cli.main(
            [
                "project",
                "create",
                "--admin-username",
                "admin",
                "--hotel-id",
                "999",
                "--name",
                "P",
            ]
        )
        == 1
    )
    assert capsys.readouterr().err == "Hotel not found.\n"
    assert (
        cli.main(
            [
                "user",
                "create",
                "--admin-username",
                "admin",
                "--username",
                "admin",
                "--display-name",
                "A",
                "--role",
                "ENGINEER",
            ]
        )
        == 1
    )
    assert capsys.readouterr().err == "Username already exists.\n"
    for session in sessions:
        session.rollback.assert_called_once()
        session.close.assert_called_once()
        session.commit.assert_not_called()
