"""add comment table

Revision ID: 81654a2185a4
Revises: e07250d000e5
Create Date: 2026-01-27 16:48:33.600668

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81654a2185a4'
down_revision: Union[str, Sequence[str], None] = 'e07250d000e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_task_id', 'comments', ['task_id'])
    op.create_index('ix_comments_user_id', 'comments', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_comments_user_id', table_name='comments')
    op.drop_index('ix_comments_task_id', table_name='comments')
    op.drop_table('comments')
