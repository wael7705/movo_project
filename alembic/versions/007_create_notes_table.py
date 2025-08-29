"""Create lightweight notes table if not exists

Revision ID: 007
Revises: 006
Create Date: 2025-08-29 00:00:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create a minimal notes table for orders/customers/restaurants/captains/issues
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = 'notes'
            ) THEN
                CREATE TABLE notes (
                    note_id SERIAL PRIMARY KEY,
                    target_type VARCHAR(20) NOT NULL,
                    reference_id INTEGER NOT NULL,
                    note_text TEXT NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_notes_target_ref ON notes(target_type, reference_id);
                CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);
            END IF;
        END$$;
        """
    )


def downgrade():
    # Keep notes data; do not drop the table on downgrade to avoid data loss
    pass


