from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Attachment
from app.repositories import AttachmentRepository
from tests.repositories.test_issue_repository import make_issue


def make_attachment(issue, user, uploaded_at, name) -> Attachment:
    return Attachment(
        issue=issue, file_name=name, original_file_name=name,
        file_path=f"issues/{name}", mime_type="image/jpeg", file_size=1,
        uploader=user, uploaded_at=uploaded_at,
    )


def test_find_list_create_delete_order_and_no_commit(database_session: Session, base_entities) -> None:
    issue = make_issue(base_entities)
    other_issue = make_issue(base_entities)
    database_session.add_all([issue, other_issue])
    database_session.flush()
    later = make_attachment(issue, base_entities["user"], base_entities["now"] + timedelta(hours=1), "later")
    first = make_attachment(issue, base_entities["user"], base_entities["now"], "first")
    second = make_attachment(issue, base_entities["user"], base_entities["now"], "second")
    excluded = make_attachment(other_issue, base_entities["user"], base_entities["now"], "excluded")
    database_session.add_all([later, first, second, excluded])
    database_session.flush()
    repository = AttachmentRepository(database_session)
    first_id = first.id
    assert repository.find_by_id(first_id) is first
    assert repository.find_by_id(99999) is None
    assert repository.list_by_issue(issue.id) == [first, second, later]
    database_session.commit()
    created = repository.create(make_attachment(issue, base_entities["user"], base_entities["now"], "created"))
    created_id = created.id
    assert created_id is not None
    repository.delete(first)
    assert database_session.get(Attachment, first_id) is None
    assert database_session.get(Attachment, second.id) is second
    database_session.rollback()
    assert database_session.get(Attachment, created_id) is None
    assert database_session.get(Attachment, first_id) is first
