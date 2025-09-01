"""Add source column to notes if not exists

    Revision ID: 008_add_notes_source_column
    Revises: 007_create_notes_table
Create Date: 2025-08-29 00:10:00.000000

"""
from alembic import op


revision = '008_add_notes_source_column'
down_revision = '007_create_notes_table'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='notes' AND column_name='source'
            ) THEN
                ALTER TABLE notes ADD COLUMN source VARCHAR(20) DEFAULT 'employee';
            END IF;
        END$$;
        """
    )


def downgrade():
    pass


