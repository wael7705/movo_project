"""Add cancelled_count column to customers table

Revision ID: 003
Revises: 002
Create Date: 2024-12-19 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add cancelled_count column to customers table if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='customers' AND column_name='cancelled_count'
            ) THEN 
                ALTER TABLE customers ADD COLUMN cancelled_count INTEGER DEFAULT 0; 
            END IF;
        END$$;
    """)


def downgrade():
    # Remove the column we added
    op.execute("ALTER TABLE customers DROP COLUMN IF EXISTS cancelled_count")

