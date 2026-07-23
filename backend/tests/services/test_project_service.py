from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import NotFoundError
from app.services import ProjectService


def test_list_projects_preserves_repository_order(domain_entities) -> None:
    first = domain_entities["project"]
    second = SimpleNamespace(
        id=9, name="Second", hotel=SimpleNamespace(id=1, name="Hotel")
    )
    repository = MagicMock()
    repository.list_all.return_value = [second, first]

    response = ProjectService(repository).list_projects(user_id=99)

    assert [project.id for project in response.projects] == [9, 2]
    repository.list_all.assert_called_once_with()


def test_validate_project_exists(domain_entities) -> None:
    repository = MagicMock()
    repository.find_by_id.return_value = domain_entities["project"]

    assert ProjectService(repository).validate_project_exists(2) is None


def test_validate_project_not_found() -> None:
    repository = MagicMock()
    repository.find_by_id.return_value = None

    with pytest.raises(NotFoundError, match="Project not found"):
        ProjectService(repository).validate_project_exists(99)
