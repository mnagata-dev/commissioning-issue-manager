"""Project application service."""

from app.core.exceptions import NotFoundError
from app.repositories.project_repository import ProjectRepository
from app.schemas import ProjectListResponse, ProjectResponse


class ProjectService:
    def __init__(self, project_repository: ProjectRepository) -> None:
        self.project_repository = project_repository

    def list_projects(self, user_id: int) -> ProjectListResponse:
        del user_id
        projects = self.project_repository.list_all()
        return ProjectListResponse(
            projects=[
                ProjectResponse(
                    id=project.id,
                    name=project.name,
                    hotel={"id": project.hotel.id, "name": project.hotel.name},
                )
                for project in projects
            ]
        )

    def validate_project_exists(self, project_id: int) -> None:
        if self.project_repository.find_by_id(project_id) is None:
            raise NotFoundError("Project not found.")
