from sqlalchemy import event
from sqlalchemy.orm import Session

from app.repositories import ProjectRepository


def test_find_and_list_projects_with_hotel(database_session: Session, base_entities) -> None:
    repository = ProjectRepository(database_session)
    database_session.expire_all()
    projects = repository.list_all()
    statement_count = 0

    def count_statements(*args) -> None:
        nonlocal statement_count
        statement_count += 1

    event.listen(database_session.bind, "before_cursor_execute", count_statements)
    try:
        assert [project.hotel.name for project in projects] == ["Hotel A", "Hotel B"]
    finally:
        event.remove(database_session.bind, "before_cursor_execute", count_statements)
    assert statement_count == 0
    assert repository.find_by_id(projects[0].id).hotel.name == "Hotel A"
    assert repository.find_by_id(99999) is None
