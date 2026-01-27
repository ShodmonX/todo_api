"""add reminder table

Revision ID: 3b5866556292
Revises: 81654a2185a4
Create Date: 2026-01-27 17:24:00.674883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b5866556292'
down_revision: Union[str, Sequence[str], None] = '81654a2185a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('reminder_time', sa.DateTime(), nullable=False),
        sa.Column('is_sent', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('ix_reminders_reminder_time', 'reminders', ['reminder_time'])
    op.create_index('ix_reminders_is_sent', 'reminders', ['is_sent'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_reminders_is_sent', table_name='reminders')
    op.drop_index('ix_reminders_reminder_time', table_name='reminders')
    op.drop_index('ix_reminders_task_id', table_name='reminders')
    op.drop_table('reminders')
