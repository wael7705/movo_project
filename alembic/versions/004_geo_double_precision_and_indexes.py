"""Geo precision and indexes

Revision ID: 004
Revises: 003
Create Date: 2025-08-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # ترقية أنواع الإحداثيات إلى double precision (بدون فقد بيانات)
    op.execute("ALTER TABLE restaurants ALTER COLUMN latitude TYPE double precision USING latitude::double precision")
    op.execute("ALTER TABLE restaurants ALTER COLUMN longitude TYPE double precision USING longitude::double precision")
    op.execute("ALTER TABLE captains ALTER COLUMN last_lat TYPE double precision USING last_lat::double precision")
    op.execute("ALTER TABLE captains ALTER COLUMN last_lng TYPE double precision USING last_lng::double precision")

    # فهارس لمواقع المطاعم والكباتن (بسيطة على الأعمدة)
    op.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_lat ON restaurants(latitude)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_restaurants_lng ON restaurants(longitude)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_captains_last_lat ON captains(last_lat)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_captains_last_lng ON captains(last_lng)")


def downgrade():
    # لا حاجة للعودة لأن double precision أدق، لكن نعيد النوع إلى numeric للحذر
    op.execute("DROP INDEX IF EXISTS idx_captains_last_lng")
    op.execute("DROP INDEX IF EXISTS idx_captains_last_lat")
    op.execute("DROP INDEX IF EXISTS idx_restaurants_lng")
    op.execute("DROP INDEX IF EXISTS idx_restaurants_lat")
    op.execute("ALTER TABLE captains ALTER COLUMN last_lng TYPE numeric(11,8) USING last_lng::numeric")
    op.execute("ALTER TABLE captains ALTER COLUMN last_lat TYPE numeric(10,8) USING last_lat::numeric")
    op.execute("ALTER TABLE restaurants ALTER COLUMN longitude TYPE numeric(11,8) USING longitude::numeric")
    op.execute("ALTER TABLE restaurants ALTER COLUMN latitude TYPE numeric(10,8) USING latitude::numeric")
