"""Attachment database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Attachment


class AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, attachment_id: int) -> Attachment | None:
        return self.session.get(Attachment, attachment_id)

    def list_by_issue(self, issue_id: int) -> list[Attachment]:
        statement = (
            select(Attachment)
            .where(Attachment.issue_id == issue_id)
            .order_by(Attachment.uploaded_at.asc(), Attachment.id.asc())
        )
        return list(self.session.scalars(statement))

    def create(self, attachment: Attachment) -> Attachment:
        self.session.add(attachment)
        self.session.flush()
        return attachment

    def delete(self, attachment: Attachment) -> None:
        self.session.delete(attachment)
        self.session.flush()
