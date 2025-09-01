"""Enable PostGIS and add GEOGRAPHY columns with GIST indexes

    Revision ID: 005_enable_postgis_and_geography
    Revises: 004_geo_double_precision_and_indexes
Create Date: 2025-08-29 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_enable_postgis_and_geography'
down_revision = '004_geo_double_precision_and_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # إذا لم تكن وحدة postgis مثبتة (في صورة postgres العادية) نتجاوز بأمان
    op.execute(
        """
DO $$
BEGIN
  BEGIN
    EXECUTE 'CREATE EXTENSION IF NOT EXISTS postgis';
  EXCEPTION WHEN others THEN
    RAISE NOTICE 'PostGIS not available; skipping migration 005 safely';
    RETURN;
  END;

  -- إضافة أعمدة GEOGRAPHY موازية دون حذف القديمة لضمان عدم الكسر
  EXECUTE 'ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS geo geography(Point,4326)';
  EXECUTE 'UPDATE restaurants SET geo = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography WHERE geo IS NULL';
  EXECUTE 'CREATE INDEX IF NOT EXISTS idx_restaurants_geo ON restaurants USING gist(geo)';

  EXECUTE 'ALTER TABLE captains ADD COLUMN IF NOT EXISTS last_geo geography(Point,4326)';
  EXECUTE 'UPDATE captains SET last_geo = ST_SetSRID(ST_MakePoint(last_lng, last_lat), 4326)::geography WHERE last_lat IS NOT NULL AND last_lng IS NOT NULL AND last_geo IS NULL';
  EXECUTE 'CREATE INDEX IF NOT EXISTS idx_captains_last_geo ON captains USING gist(last_geo)';
END$$;
        """
    )


def downgrade():
    # إزالة الفهارس والأعمدة الجغرافية فقط
    op.execute("DROP INDEX IF EXISTS idx_captains_last_geo")
    op.execute("ALTER TABLE captains DROP COLUMN IF EXISTS last_geo")
    op.execute("DROP INDEX IF EXISTS idx_restaurants_geo")
    op.execute("ALTER TABLE restaurants DROP COLUMN IF EXISTS geo")
