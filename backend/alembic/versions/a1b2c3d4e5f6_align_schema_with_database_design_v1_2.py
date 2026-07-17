"""align schema with database design v1.2

Revision ID: a1b2c3d4e5f6
Revises: 77d0a0dc1ce3
Create Date: 2026-07-17
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "77d0a0dc1ce3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


role = sa.Enum(
    "ADMINISTRATOR", "ENGINEER", name="role", native_enum=False,
    create_constraint=True,
)
target_type = sa.Enum(
    "ROOM", "OTHER", name="target_type", native_enum=False,
    create_constraint=True,
)
category = sa.Enum(
    "LIGHTING", "SHADE", "KEYPAD", "SENSOR", "TSTAT", "PROCESSOR",
    "NETWORK", "SERVER", "INTEGRATION", "OTHER", name="category",
    native_enum=False, create_constraint=True,
)
status = sa.Enum(
    "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED", name="status",
    native_enum=False, create_constraint=True,
)


def upgrade() -> None:
    """Upgrade schema to the current database design."""
    op.drop_table("projects")
    op.drop_table("hotels")
    op.drop_table("users")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("role", role, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_table(
        "hotels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_hotels"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"], ["hotels.id"], name="fk_projects_hotel_id_hotels"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
    )
    op.create_index("ix_projects_hotel_id", "projects", ["hotel_id"])
    op.create_table(
        "room_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"], ["hotels.id"], name="fk_room_types_hotel_id_hotels"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_room_types"),
    )
    op.create_index("ix_room_types_hotel_id", "room_types", ["hotel_id"])
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("room_type_id", sa.Integer(), nullable=False),
        sa.Column("room_number", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"], ["hotels.id"], name="fk_rooms_hotel_id_hotels"
        ),
        sa.ForeignKeyConstraint(
            ["room_type_id"], ["room_types.id"],
            name="fk_rooms_room_type_id_room_types",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_rooms"),
        sa.UniqueConstraint(
            "hotel_id", "room_number", name="uq_rooms_hotel_id_room_number"
        ),
    )
    op.create_index("ix_rooms_hotel_id", "rooms", ["hotel_id"])
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=True),
        sa.Column("target_type", target_type, nullable=False),
        sa.Column("target", sa.Text(), nullable=True),
        sa.Column("category", category, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], name="fk_issues_project_id_projects"
        ),
        sa.ForeignKeyConstraint(
            ["room_id"], ["rooms.id"], name="fk_issues_room_id_rooms"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_issues_created_by_users"
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], name="fk_issues_updated_by_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_issues"),
    )
    for column in ("project_id", "room_id", "status", "category", "target_type"):
        op.create_index(f"ix_issues_{column}", "issues", [column])
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["issues.id"], name="fk_comments_issue_id_issues"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name="fk_comments_created_by_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
    )
    op.create_index("ix_comments_issue_id", "comments", ["issue_id"])
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("original_file_name", sa.Text(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.Text(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("file_size > 0", name="ck_attachments_file_size_positive"),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["issues.id"], name="fk_attachments_issue_id_issues"
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"], ["users.id"], name="fk_attachments_uploaded_by_users"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_attachments"),
    )
    op.create_index("ix_attachments_issue_id", "attachments", ["issue_id"])


def downgrade() -> None:
    """Downgrade schema to the previous revision."""
    op.drop_table("attachments")
    op.drop_table("comments")
    op.drop_table("issues")
    op.drop_table("rooms")
    op.drop_table("room_types")
    op.drop_table("projects")
    op.drop_table("hotels")
    op.drop_table("users")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_table(
        "hotels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_hotels_id", "hotels", ["id"])
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.ForeignKeyConstraint(["hotel_id"], ["hotels.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_projects_id", "projects", ["id"])
