from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Category, Issue, Status, TargetType
from app.repositories import IssueRepository


def make_issue(base, **overrides) -> Issue:
    values = {
        "project": base["project"], "room": base["room"],
        "target_type": TargetType.ROOM, "target": None,
        "category": Category.LIGHTING, "description": "lighting issue",
        "status": Status.OPEN, "creator": base["user"], "updater": base["user"],
        "created_at": base["now"], "updated_at": base["now"],
    }
    values.update(overrides)
    return Issue(**values)


def test_find_filters_count_pagination_and_order(database_session: Session, base_entities) -> None:
    repository = IssueRepository(database_session)
    older = make_issue(base_entities, description="lighting keypad")
    newer = make_issue(
        base_entities, category=Category.KEYPAD, status=Status.IN_PROGRESS,
        description="keypad failure", updated_at=base_entities["now"] + timedelta(hours=1),
    )
    tied = make_issue(base_entities)
    other = make_issue(base_entities, project=base_entities["other_project"], room=None)
    database_session.add_all([older, newer, tied, other])
    database_session.flush()
    project_id = base_entities["project"].id
    assert repository.find_by_id(older.id) is older
    assert repository.find_by_id(99999) is None
    assert repository.list_by_project(project_id, None, None, None, None, 0, 10) == [newer, tied, older]
    assert repository.list_by_project(project_id, None, None, None, None, 1, 1) == [tied]
    assert repository.count_by_project(project_id, None, None, None, None) == 3
    assert repository.count_by_project(project_id, "IN_PROGRESS", None, None, None) == 1
    assert repository.count_by_project(project_id, None, "KEYPAD", None, None) == 1
    assert repository.count_by_project(project_id, None, None, "ROOM", None) == 3
    assert repository.count_by_project(project_id, None, None, None, "keypad") == 2
    assert repository.list_by_project(project_id, "IN_PROGRESS", None, None, None, 0, 10) == [newer]
    assert repository.list_by_project(project_id, None, "KEYPAD", None, None, 0, 10) == [newer]
    assert repository.list_by_project(project_id, None, None, "ROOM", None, 0, 10) == [newer, tied, older]
    assert repository.list_by_project(project_id, None, None, None, "keypad", 0, 10) == [newer, older]
    assert repository.count_by_project(project_id, "IN_PROGRESS", "KEYPAD", "ROOM", "failure") == 1


def test_create_update_and_no_commit(database_session: Session, base_entities) -> None:
    repository = IssueRepository(database_session)
    issue = repository.create(make_issue(base_entities))
    issue_id = issue.id
    assert issue_id is not None
    issue.description = "changed"
    assert repository.update(issue) is issue
    database_session.expire(issue, ["description"])
    assert issue.description == "changed"
    database_session.rollback()
    assert database_session.get(Issue, issue_id) is None
