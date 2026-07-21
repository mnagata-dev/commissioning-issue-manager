"""Project database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Project


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, project_id: int) -> Project | None:
        statement = (
            select(Project)
            .options(joinedload(Project.hotel))
            .where(Project.id == project_id)
        )
        return self.session.scalar(statement)

    def list_all(self) -> list[Project]:
        statement = (
            select(Project)
            .options(joinedload(Project.hotel))
            .order_by(Project.id.asc())
        )
        return list(self.session.scalars(statement))
