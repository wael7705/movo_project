"""add visibility flags for restaurants and options

Revision ID: 009_admin_visibility_flags
Revises: 008_add_notes_source_column
Create Date: 2025-08-29
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_admin_visibility_flags'
down_revision = '008_add_notes_source_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('restaurants') as batch:
        batch.add_column(sa.Column('visible', sa.Boolean(), nullable=False, server_default=sa.true()))
    # menu_items already has is_visible in seed, ensure exists (no-op if present)
    try:
        with op.batch_alter_table('menu_items') as batch:
            batch.add_column(sa.Column('is_visible', sa.Boolean(), nullable=False, server_default=sa.true()))
    except Exception:
        pass
    # menu_item_options availability column
    try:
        with op.batch_alter_table('menu_item_options') as batch:
            batch.add_column(sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.true()))
    except Exception:
        pass


def downgrade() -> None:
    try:
        with op.batch_alter_table('menu_item_options') as batch:
            batch.drop_column('is_available')
    except Exception:
        pass
    try:
        with op.batch_alter_table('menu_items') as batch:
            batch.drop_column('is_visible')
    except Exception:
        pass
    with op.batch_alter_table('restaurants') as batch:
        batch.drop_column('visible')


