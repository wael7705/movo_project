"""Idempotency keys and order events log

    Revision ID: 006_idempotency_and_order_events
    Revises: 005_enable_postgis_and_geography
Create Date: 2025-08-29 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_idempotency_and_order_events'
down_revision = '005_enable_postgis_and_geography'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
CREATE TABLE IF NOT EXISTS idempotency_keys (
  key TEXT PRIMARY KEY,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_events (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_order_events_order_id ON order_events(order_id);
        """
    )


def downgrade():
    op.execute("DROP TABLE IF EXISTS order_events")
    op.execute("DROP TABLE IF EXISTS idempotency_keys")
