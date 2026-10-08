"""Isolated administration test dependencies."""

from collections.abc import Callable, Generator

import pytest
from sqlalchemy import Engine, event
from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories import (
    HotelRepository,
    ProjectRepository,
    RoomRepository,
    RoomTypeRepository,
    UserRepository,
)
from app.schemas.administration import BootstrapAdminRequest
from app.services.administration_service import AdministrationService
from app.services.auth_service import AuthService


def make_service(session: Session) -> AdministrationService:
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


@pytest.fixture
def administration_engine(database_engine: Engine) -> Engine:
    @event.listens_for(database_engine, "connect")
    def enable_foreign_keys(connection, record) -> None:
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(database_engine)
    return database_engine


@pytest.fixture
def service_factory(
    administration_engine: Engine,
) -> Callable[[], AdministrationService]:
    def create() -> AdministrationService:
        return make_service(Session(administration_engine, expire_on_commit=False))

    return create


@pytest.fixture
def service(service_factory) -> Generator[AdministrationService, None, None]:
    instance = service_factory()
    try:
        yield instance
    finally:
        instance.session.close()


@pytest.fixture
def admin_id(service: AdministrationService) -> int:
    result = service.bootstrap_admin(
        BootstrapAdminRequest(
            username="admin",
            display_name="Administrator",
            password="admin-pass",
        )
    )
    return result.id
