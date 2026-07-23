"""Issue application service."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Category, Issue, Project, Room, Status, TargetType, User
from app.repositories import (
    AttachmentRepository,
    CommentRepository,
    IssueRepository,
    ProjectRepository,
    RoomRepository,
    UserRepository,
)
from app.schemas import (
    AttachmentResponse,
    CommentResponse,
    CreateIssueRequest,
    IssueDetailResponse,
    IssueSummaryResponse,
    UpdateIssueRequest,
    UpdateIssueStatusRequest,
)


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class IssueService:
    def __init__(
        self,
        session: Session,
        project_repository: ProjectRepository,
        room_repository: RoomRepository,
        issue_repository: IssueRepository,
        user_repository: UserRepository,
        comment_repository: CommentRepository,
        attachment_repository: AttachmentRepository,
    ) -> None:
        self.session = session
        self.project_repository = project_repository
        self.room_repository = room_repository
        self.issue_repository = issue_repository
        self.user_repository = user_repository
        self.comment_repository = comment_repository
        self.attachment_repository = attachment_repository

    def list_issues(
        self,
        project_id: int,
        status: str | None,
        category: str | None,
        target_type: str | None,
        keyword: str | None,
        page: int,
        page_size: int,
    ) -> list[IssueSummaryResponse]:
        self._require_project(project_id)
        if page < 1:
            raise ValidationError("Page must be at least 1.")
        if page_size < 1:
            raise ValidationError("Page size must be at least 1.")
        self._validate_optional_enum(status, Status, "Status")
        self._validate_optional_enum(category, Category, "Category")
        self._validate_optional_enum(target_type, TargetType, "Target type")

        issues = self.issue_repository.list_by_project(
            project_id,
            status,
            category,
            target_type,
            keyword,
            (page - 1) * page_size,
            page_size,
        )
        return [self._to_summary(issue) for issue in issues]

    def get_issue_detail(self, issue_id: int) -> IssueDetailResponse:
        issue = self._require_issue(issue_id)
        comments = self.comment_repository.list_by_issue(issue_id)
        attachments = self.attachment_repository.list_by_issue(issue_id)
        return IssueDetailResponse(
            id=issue.id,
            project={"id": issue.project.id, "name": issue.project.name},
            room=self._room_reference(issue.room),
            target_type=issue.target_type.value,
            target=issue.target,
            category=issue.category.value,
            description=issue.description,
            status=issue.status.value,
            created_by={
                "id": issue.creator.id,
                "display_name": issue.creator.display_name,
            },
            updated_by={
                "id": issue.updater.id,
                "display_name": issue.updater.display_name,
            },
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            comments=[
                CommentResponse(
                    id=comment.id,
                    comment=comment.comment,
                    created_by={
                        "id": comment.creator.id,
                        "display_name": comment.creator.display_name,
                    },
                    created_at=comment.created_at,
                )
                for comment in comments
            ],
            attachments=[
                AttachmentResponse(
                    id=attachment.id,
                    file_name=attachment.file_name,
                    mime_type=attachment.mime_type,
                    file_size=attachment.file_size,
                    uploaded_at=attachment.uploaded_at,
                )
                for attachment in attachments
            ],
        )

    def create_issue(
        self, project_id: int, request: CreateIssueRequest, user_id: int
    ) -> int:
        try:
            project = self._require_project(project_id)
            user = self._require_user(user_id)
            target_type = self._parse_enum(request.target_type, TargetType, "Target type")
            category = self._parse_enum(request.category, Category, "Category")
            room = self._validate_target(
                project, target_type, request.room_id, request.target
            )
            self._validate_description(request.description)
            timestamp = _utc_now_naive()
            issue = Issue(
                project=project,
                room=room,
                target_type=target_type,
                target=request.target,
                category=category,
                description=request.description,
                status=Status.OPEN,
                creator=user,
                updater=user,
                created_at=timestamp,
                updated_at=timestamp,
            )
            created = self.issue_repository.create(issue)
            self.session.commit()
            return created.id
        except Exception:
            self.session.rollback()
            raise

    def update_issue(
        self, issue_id: int, request: UpdateIssueRequest, user_id: int
    ) -> None:
        try:
            issue = self._require_issue(issue_id)
            user = self._require_user(user_id)
            target_type = self._parse_enum(request.target_type, TargetType, "Target type")
            category = self._parse_enum(request.category, Category, "Category")
            room = self._validate_target(
                issue.project, target_type, request.room_id, request.target
            )
            self._validate_description(request.description)
            issue.room = room
            issue.target_type = target_type
            issue.target = request.target
            issue.category = category
            issue.description = request.description
            issue.updater = user
            issue.updated_at = _utc_now_naive()
            self.issue_repository.update(issue)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def update_status(
        self, issue_id: int, request: UpdateIssueStatusRequest, user_id: int
    ) -> None:
        try:
            issue = self._require_issue(issue_id)
            user = self._require_user(user_id)
            status = self._parse_enum(request.status, Status, "Status")
            issue.status = status
            issue.updater = user
            issue.updated_at = _utc_now_naive()
            self.issue_repository.update(issue)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def _require_project(self, project_id: int) -> Project:
        project = self.project_repository.find_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found.")
        return project

    def _require_issue(self, issue_id: int) -> Issue:
        issue = self.issue_repository.find_by_id(issue_id)
        if issue is None:
            raise NotFoundError("Issue not found.")
        return issue

    def _require_user(self, user_id: int) -> User:
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    def _require_room(self, room_id: int) -> Room:
        room = self.room_repository.find_by_id(room_id)
        if room is None:
            raise NotFoundError("Room not found.")
        return room

    def _validate_target(
        self,
        project: Project,
        target_type: TargetType,
        room_id: int | None,
        target: str | None,
    ) -> Room | None:
        if target_type is TargetType.ROOM:
            if room_id is None or target is not None:
                raise ValidationError("ROOM requires a room and no target.")
            room = self._require_room(room_id)
            if room.hotel_id != project.hotel_id:
                raise ValidationError("Room does not belong to the Project hotel.")
            return room
        if room_id is not None or target is None or target == "":
            raise ValidationError("OTHER requires a target and no room.")
        return None

    @staticmethod
    def _validate_description(description: str) -> None:
        if description == "":
            raise ValidationError("Description must not be empty.")

    @staticmethod
    def _parse_enum(value: str, enum_type: type, label: str):
        try:
            return enum_type(value)
        except ValueError as error:
            raise ValidationError(f"Invalid {label.lower()}.") from error

    @classmethod
    def _validate_optional_enum(cls, value: str | None, enum_type: type, label: str) -> None:
        if value is not None:
            cls._parse_enum(value, enum_type, label)

    @staticmethod
    def _room_reference(room: Room | None) -> dict[str, int | str] | None:
        if room is None:
            return None
        return {"id": room.id, "room_number": room.room_number}

    @classmethod
    def _to_summary(cls, issue: Issue) -> IssueSummaryResponse:
        return IssueSummaryResponse(
            id=issue.id,
            room=cls._room_reference(issue.room),
            target_type=issue.target_type.value,
            target=issue.target,
            category=issue.category.value,
            description=issue.description,
            status=issue.status.value,
            updated_at=issue.updated_at,
        )
