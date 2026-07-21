from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Comment
from app.repositories import CommentRepository
from tests.repositories.test_issue_repository import make_issue


def test_list_create_order_and_no_commit(database_session: Session, base_entities) -> None:
    issue = make_issue(base_entities)
    other_issue = make_issue(base_entities)
    database_session.add_all([issue, other_issue])
    database_session.flush()
    later = Comment(issue=issue, comment="later", creator=base_entities["user"], created_at=base_entities["now"] + timedelta(hours=1))
    first = Comment(issue=issue, comment="first", creator=base_entities["user"], created_at=base_entities["now"])
    second = Comment(issue=issue, comment="second", creator=base_entities["user"], created_at=base_entities["now"])
    excluded = Comment(issue=other_issue, comment="excluded", creator=base_entities["user"], created_at=base_entities["now"])
    database_session.add_all([later, first, second, excluded])
    database_session.flush()
    repository = CommentRepository(database_session)
    assert repository.list_by_issue(issue.id) == [first, second, later]
    created = repository.create(Comment(issue=issue, comment="new", creator=base_entities["user"], created_at=base_entities["now"]))
    created_id = created.id
    assert created_id is not None
    database_session.rollback()
    assert database_session.get(Comment, created_id) is None
