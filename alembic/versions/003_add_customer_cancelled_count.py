"""Add cancelled_count column to customers table

    Revision ID: 003_add_customer_cancelled_count
    Revises: 002_add_missing_columns
Create Date: 2024-12-19 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_customer_cancelled_count'
down_revision = '002_add_missing_columns'
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

