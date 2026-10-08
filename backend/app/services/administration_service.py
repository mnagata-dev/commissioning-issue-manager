"""Authenticated administration commands and transaction management."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AuthorizationError, BusinessRuleError, NotFoundError
from app.core.security import hash_password
from app.db.session import begin_user_write_transaction
from app.models import Hotel, Project, Role, Room, RoomType, User
from app.repositories import (
    HotelRepository,
    ProjectRepository,
    RoomRepository,
    RoomTypeRepository,
    UserRepository,
)
from app.schemas.administration import (
    AdministrationResult,
    BootstrapAdminRequest,
    CreateHotelRequest,
    CreateProjectRequest,
    CreateRoomRequest,
    CreateRoomTypeRequest,
    CreateUserRequest,
    UpdateHotelRequest,
    UpdateInput,
    UpdateProjectRequest,
    UpdateRoomRequest,
    UpdateRoomTypeRequest,
    UpdateUserRequest,
)
from app.services.auth_service import AuthService

type ManagedEntity = Hotel | Project | RoomType | Room | User


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AdministrationService:
    """Apply administration rules using repositories sharing one Session."""

    def __init__(
        self,
        session: Session,
        auth_service: AuthService,
        hotel_repository: HotelRepository,
        project_repository: ProjectRepository,
        room_type_repository: RoomTypeRepository,
        room_repository: RoomRepository,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.auth_service = auth_service
        self.hotel_repository = hotel_repository
        self.project_repository = project_repository
        self.room_type_repository = room_type_repository
        self.room_repository = room_repository
        self.user_repository = user_repository

    @contextmanager
    def _command(
        self, username: str, password: str, *, user_write: bool = False
    ) -> Iterator[None]:
        try:
            if user_write:
                begin_user_write_transaction(self.session)
            current_user = self.auth_service.login(username, password)
            if current_user.role != Role.ADMINISTRATOR.value:
                raise AuthorizationError()
            yield
            self.session.commit()
        except BaseException:
            self.session.rollback()
            raise

    def create_hotel(
        self, username: str, password: str, request: CreateHotelRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            now = _utc_now_naive()
            hotel = Hotel(name=request.name, created_at=now, updated_at=now)
            self.hotel_repository.create(hotel)
            return self._result("hotel", hotel, "create")

    def update_hotel(
        self, username: str, password: str, hotel_id: int, request: UpdateHotelRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            hotel = self._require_hotel(hotel_id)
            if self._apply_update(hotel, request):
                self.hotel_repository.update(hotel)
            return self._result("hotel", hotel, "update")

    def create_project(
        self, username: str, password: str, request: CreateProjectRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            self._require_hotel(request.hotel_id)
            now = _utc_now_naive()
            project = Project(**request.model_dump(), created_at=now, updated_at=now)
            self.project_repository.create(project)
            return self._result("project", project, "create")

    def update_project(
        self,
        username: str,
        password: str,
        project_id: int,
        request: UpdateProjectRequest,
    ) -> AdministrationResult:
        with self._command(username, password):
            project = self.project_repository.find_by_id(project_id)
            if project is None:
                raise NotFoundError("Project not found.")
            if self._apply_update(project, request):
                self.project_repository.update(project)
            return self._result("project", project, "update")

    def create_room_type(
        self, username: str, password: str, request: CreateRoomTypeRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            self._require_hotel(request.hotel_id)
            now = _utc_now_naive()
            room_type = RoomType(**request.model_dump(), created_at=now, updated_at=now)
            self.room_type_repository.create(room_type)
            return self._result("room-type", room_type, "create")

    def update_room_type(
        self,
        username: str,
        password: str,
        room_type_id: int,
        request: UpdateRoomTypeRequest,
    ) -> AdministrationResult:
        with self._command(username, password):
            room_type = self.room_type_repository.find_by_id(room_type_id)
            if room_type is None:
                raise NotFoundError("Room type not found.")
            if self._apply_update(room_type, request):
                self.room_type_repository.update(room_type)
            return self._result("room-type", room_type, "update")

    def create_room(
        self, username: str, password: str, request: CreateRoomRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            self._validate_room_type(request.hotel_id, request.room_type_id)
            self._validate_room_number(request.hotel_id, request.room_number)
            now = _utc_now_naive()
            room = Room(**request.model_dump(), created_at=now, updated_at=now)
            self.room_repository.create(room)
            return self._result("room", room, "create")

    def update_room(
        self, username: str, password: str, room_id: int, request: UpdateRoomRequest
    ) -> AdministrationResult:
        with self._command(username, password):
            room = self.room_repository.find_by_id(room_id)
            if room is None:
                raise NotFoundError("Room not found.")
            changes = request.model_dump(exclude_unset=True)
            self._validate_room_type(
                room.hotel_id, changes.get("room_type_id", room.room_type_id)
            )
            self._validate_room_number(
                room.hotel_id, changes.get("room_number", room.room_number), room.id
            )
            if self._apply_update(room, request):
                self.room_repository.update(room)
            return self._result("room", room, "update")

    def create_user(
        self, username: str, password: str, request: CreateUserRequest
    ) -> AdministrationResult:
        with self._command(username, password, user_write=True):
            self._validate_username(request.username)
            user = self._new_user(request, request.role)
            self.user_repository.create(user)
            return self._result("user", user, "create")

    def update_user(
        self, username: str, password: str, user_id: int, request: UpdateUserRequest
    ) -> AdministrationResult:
        with self._command(username, password, user_write=True):
            user = self.user_repository.find_by_id(user_id)
            if user is None:
                raise NotFoundError("User not found.")
            if "username" in request.model_fields_set:
                self._validate_username(request.username, user.id)
            if user.role == Role.ADMINISTRATOR and request.role == Role.ENGINEER:
                if self.user_repository.count_by_role(Role.ADMINISTRATOR) <= 1:
                    raise BusinessRuleError("At least one Administrator must remain.")
            if self._apply_update(user, request):
                self.user_repository.update(user)
            return self._result("user", user, "update")

    def bootstrap_admin(self, request: BootstrapAdminRequest) -> AdministrationResult:
        try:
            begin_user_write_transaction(self.session)
            if self.user_repository.count_all() != 0:
                raise BusinessRuleError("Bootstrap requires an empty User table.")
            user = self._new_user(request, Role.ADMINISTRATOR)
            self.user_repository.create(user)
            result = self._result("user", user, "bootstrap-admin")
            self.session.commit()
            return result
        except BaseException:
            self.session.rollback()
            raise

    def _require_hotel(self, hotel_id: int) -> Hotel:
        hotel = self.hotel_repository.find_by_id(hotel_id)
        if hotel is None:
            raise NotFoundError("Hotel not found.")
        return hotel

    def _validate_room_type(self, hotel_id: int, room_type_id: int) -> None:
        self._require_hotel(hotel_id)
        room_type = self.room_type_repository.find_by_id(room_type_id)
        if room_type is None:
            raise NotFoundError("Room type not found.")
        if room_type.hotel_id != hotel_id:
            raise BusinessRuleError("Room type must belong to the same Hotel.")

    def _validate_room_number(
        self, hotel_id: int, room_number: str, room_id: int | None = None
    ) -> None:
        existing = self.room_repository.find_by_hotel_and_room_number(
            hotel_id, room_number
        )
        if existing is not None and existing.id != room_id:
            raise BusinessRuleError("Room number already exists in this Hotel.")

    def _validate_username(self, username: str, user_id: int | None = None) -> None:
        existing = self.user_repository.find_by_username(username)
        if existing is not None and existing.id != user_id:
            raise BusinessRuleError("Username already exists.")

    @staticmethod
    def _new_user(request: BootstrapAdminRequest, role: Role) -> User:
        now = _utc_now_naive()
        return User(
            username=request.username,
            display_name=request.display_name,
            password_hash=hash_password(request.password),
            role=role,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _apply_update(entity: ManagedEntity, request: UpdateInput) -> bool:
        changes = request.model_dump(exclude_unset=True)
        if not changes:
            return False
        if "password" in changes:
            changes["password_hash"] = hash_password(changes.pop("password"))
        for name, value in changes.items():
            setattr(entity, name, value)
        entity.updated_at = _utc_now_naive()
        return True

    @staticmethod
    def _result(
        target: str, entity: ManagedEntity, operation: str
    ) -> AdministrationResult:
        return AdministrationResult(target=target, id=entity.id, operation=operation)
