"""Run administration commands with python -m app.cli."""

import argparse
import getpass
import sys
import warnings
from typing import TYPE_CHECKING

from pydantic import ValidationError as SchemaValidationError

from app.core.exceptions import ApplicationError
from app.models.enums import Role
from app.schemas.administration import (
    BootstrapAdminRequest,
    CreateHotelRequest,
    CreateProjectRequest,
    CreateRoomRequest,
    CreateRoomTypeRequest,
    CreateUserRequest,
    UpdateHotelRequest,
    UpdateProjectRequest,
    UpdateRoomRequest,
    UpdateRoomTypeRequest,
    UpdateUserRequest,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.services.administration_service import AdministrationService


class CommandParser(argparse.ArgumentParser):
    """Do not echo supplied values, which may include misplaced secrets."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, "Invalid command arguments. Use --help for usage.\n")


def build_parser() -> argparse.ArgumentParser:
    """Define only the approved administration commands and options."""
    parser = CommandParser(prog="python -m app.cli", allow_abbrev=False)
    targets = parser.add_subparsers(dest="target", required=True)
    for target in ("hotel", "project", "room-type", "room", "user"):
        target_parser = targets.add_parser(target, allow_abbrev=False)
        operations = target_parser.add_subparsers(dest="operation", required=True)
        for operation in ("create", "update"):
            command = operations.add_parser(operation, allow_abbrev=False)
            command.add_argument("--admin-username", required=True)
            creating = operation == "create"
            if not creating:
                command.add_argument("id", type=int)
            if target in ("hotel", "project", "room-type"):
                command.add_argument(
                    "--name", required=creating, default=argparse.SUPPRESS
                )
            if creating and target in ("project", "room-type", "room"):
                command.add_argument("--hotel-id", type=int, required=True)
            if target == "room":
                command.add_argument(
                    "--room-type-id",
                    type=int,
                    required=creating,
                    default=argparse.SUPPRESS,
                )
                command.add_argument(
                    "--room-number", required=creating, default=argparse.SUPPRESS
                )
                command.add_argument("--display-name", default=argparse.SUPPRESS)
            if target == "user":
                command.add_argument(
                    "--username", required=creating, default=argparse.SUPPRESS
                )
                command.add_argument(
                    "--display-name", required=creating, default=argparse.SUPPRESS
                )
                command.add_argument(
                    "--role",
                    choices=[role.value for role in Role],
                    required=creating,
                    default=argparse.SUPPRESS,
                )
                if not creating:
                    command.add_argument("--set-password", action="store_true")
        if target == "user":
            bootstrap = operations.add_parser("bootstrap-admin", allow_abbrev=False)
            bootstrap.add_argument("--username", required=True)
            bootstrap.add_argument("--display-name", required=True)
    return parser


def _read_password(prompt: str) -> str:
    with warnings.catch_warnings():
        warnings.simplefilter("error", getpass.GetPassWarning)
        return getpass.getpass(prompt)


def _build_service(session: "Session") -> "AdministrationService":
    from app.repositories import (
        HotelRepository,
        ProjectRepository,
        RoomRepository,
        RoomTypeRepository,
        UserRepository,
    )
    from app.services.administration_service import AdministrationService
    from app.services.auth_service import AuthService

    users = UserRepository(session)
    return AdministrationService(
        session,
        AuthService(users),
        HotelRepository(session),
        ProjectRepository(session),
        RoomTypeRepository(session),
        RoomRepository(session),
        users,
    )


def main(argv: list[str] | None = None) -> int:
    """Parse, collect secrets, execute one transaction, and report safe output."""
    args = build_parser().parse_args(argv)
    try:
        values = vars(args).copy()
        target = values.pop("target")
        operation = values.pop("operation")
        admin_username = values.pop("admin_username", "")
        target_id = values.pop("id", None)
        set_password = values.pop("set_password", False)
        admin_password = ""
        if operation != "bootstrap-admin":
            admin_password = _read_password("Administrator password: ")
        if target == "user" and (operation != "update" or set_password):
            values["password"] = _read_password("New User password: ")

        schemas = {
            ("hotel", "create"): CreateHotelRequest,
            ("hotel", "update"): UpdateHotelRequest,
            ("project", "create"): CreateProjectRequest,
            ("project", "update"): UpdateProjectRequest,
            ("room-type", "create"): CreateRoomTypeRequest,
            ("room-type", "update"): UpdateRoomTypeRequest,
            ("room", "create"): CreateRoomRequest,
            ("room", "update"): UpdateRoomRequest,
            ("user", "create"): CreateUserRequest,
            ("user", "update"): UpdateUserRequest,
            ("user", "bootstrap-admin"): BootstrapAdminRequest,
        }
        request = schemas[target, operation](**values)
        from app.db.session import SessionLocal

        session = SessionLocal()
        try:
            service = _build_service(session)
            if operation == "bootstrap-admin":
                result = service.bootstrap_admin(request)
            else:
                method_name = f"{operation}_{target.replace('-', '_')}"
                method = getattr(service, method_name)
                if operation == "update":
                    result = method(admin_username, admin_password, target_id, request)
                else:
                    result = method(admin_username, admin_password, request)
        finally:
            session.close()
        print(f"{result.target} {result.id}: {result.operation} succeeded.")
        return 0
    except ApplicationError as error:
        print(error.message, file=sys.stderr)
    except SchemaValidationError:
        print("Invalid administration input.", file=sys.stderr)
    except getpass.GetPassWarning, EOFError, KeyboardInterrupt:
        print("Hidden password input unavailable or interrupted.", file=sys.stderr)
    except Exception:
        print("Administration command failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
