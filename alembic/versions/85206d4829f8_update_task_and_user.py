"""update Task and User

Revision ID: 85206d4829f8
Revises: 6c3e795d582e
Create Date: 2026-01-08 15:20:33.721892
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '85206d4829f8'
down_revision: Union[str, Sequence[str], None] = '6c3e795d582e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("ALTER TABLE tasks ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority DROP DEFAULT")

    task_status = postgresql.ENUM('pending', 'in_progress', 'completed', name='task_status')
    task_status.create(op.get_bind(), checkfirst=True)

    tasks_priority = postgresql.ENUM('low', 'medium', 'high', name='tasks_priority')
    tasks_priority.create(op.get_bind(), checkfirst=True)

    op.alter_column('tasks', 'status',
               type_=task_status,
               existing_type=sa.VARCHAR(length=25),
               existing_nullable=False,
               postgresql_using="status::task_status")

    op.alter_column('tasks', 'priority',
               type_=tasks_priority,
               existing_type=sa.VARCHAR(length=25),
               existing_nullable=False,
               postgresql_using="priority::tasks_priority")

    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'pending'")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority SET DEFAULT 'low'")

    op.alter_column('tasks', 'due_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.alter_column('users', 'timezone',
               existing_type=sa.VARCHAR(length=255),
               nullable=False,
               existing_server_default=sa.text("'Asia/Tashkent'::character varying"))

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("ALTER TABLE tasks ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority DROP DEFAULT")

    op.alter_column('tasks', 'status',
               type_=sa.VARCHAR(length=25),
               postgresql_using="status::varchar")

    op.alter_column('tasks', 'priority',
               type_=sa.VARCHAR(length=25),
               postgresql_using="priority::varchar")

    task_status = postgresql.ENUM('pending', 'in_progress', 'completed', name='task_status')
    task_status.drop(op.get_bind(), checkfirst=True)

    tasks_priority = postgresql.ENUM('low', 'medium', 'high', name='tasks_priority')
    tasks_priority.drop(op.get_bind(), checkfirst=True)

    op.execute("ALTER TABLE tasks ALTER COLUMN status SET DEFAULT 'pending'")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority SET DEFAULT 'low'")

    op.alter_column('tasks', 'due_date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    op.alter_column('users', 'timezone',
               existing_type=sa.VARCHAR(length=255),
               nullable=True,
               existing_server_default=sa.text("'Asia/Tashkent'::character varying"))

    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
