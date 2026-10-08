"""User database access."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Role, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def find_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.scalar(statement)

    def create(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def update(self, user: User) -> User:
        self.session.flush()
        return user

    def count_all(self) -> int:
        return self.session.scalar(select(func.count(User.id))) or 0

    def count_by_role(self, role: Role) -> int:
        statement = select(func.count(User.id)).where(User.role == role)
        return self.session.scalar(statement) or 0
