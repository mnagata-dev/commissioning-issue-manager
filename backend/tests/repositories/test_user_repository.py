from sqlalchemy.orm import Session

from app.repositories import UserRepository


def test_find_user(database_session: Session, base_entities) -> None:
    repository = UserRepository(database_session)
    user = base_entities["user"]
    assert repository.find_by_id(user.id) is user
    assert repository.find_by_username("engineer") is user
    assert repository.find_by_id(99999) is None
    assert repository.find_by_username("missing") is None
