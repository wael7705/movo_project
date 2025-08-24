"""Add missing columns to orders table

Revision ID: 002
Revises: 001
Create Date: 2024-12-19 22:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns that exist in the model but not in the database
    op.execute("""
        DO $$ 
        BEGIN 
            -- Add current_stage_name column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='orders' AND column_name='current_stage_name'
            ) THEN 
                ALTER TABLE orders ADD COLUMN current_stage_name VARCHAR(50); 
            END IF;
            
            -- Add cancel_count_per_day column if it doesn't exist
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='orders' AND column_name='cancel_count_per_day'
            ) THEN 
                ALTER TABLE orders ADD COLUMN cancel_count_per_day INTEGER DEFAULT 0; 
            END IF;
        END$$;
    """)


def downgrade():
    # Remove the columns we added
    op.execute("ALTER TABLE orders DROP COLUMN IF EXISTS current_stage_name")
    op.execute("ALTER TABLE orders DROP COLUMN IF EXISTS cancel_count_per_day")

