"""Enforce single active status, normalize enum, and fix demo creation

    Revision ID: 001_enforce_status_enum_and_normalize
    Revises: 
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_enforce_status_enum_and_normalize'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1) تطبيع البيانات الحالية (lowercase + map issue→problem)
    op.execute("UPDATE orders SET status = LOWER(TRIM(status))")
    op.execute("UPDATE orders SET status = 'problem' WHERE status IN ('issue','Issue','ISSUE')")
    
    # Map old status values to new ones for compatibility
    op.execute("UPDATE orders SET status = 'choose_captain' WHERE status IN ('accepted', 'waiting_restaurant_acceptance')")
    op.execute("UPDATE orders SET status = 'processing' WHERE status IN ('preparing', 'pick_up_ready')")
    
    # 2) قيمة افتراضية وضبط عدم السماح بالقيم الفارغة
    op.execute("ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending'")
    
    # 3) قيود Enum صارمة
    op.execute("""
        ALTER TABLE orders ADD CONSTRAINT orders_status_check 
        CHECK (status IN (
            'pending','choose_captain','processing','out_for_delivery','delivered','cancelled','problem'
        ))
    """)
    
    # 4) تأكد من وجود حقول مساعدة (إن لم تكن موجودة)
    # is_deferred boolean يستخدم فقط لتحديد قفزة next من pending إلى processing
    op.execute("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='orders' AND column_name='is_deferred'
            ) THEN 
                ALTER TABLE orders ADD COLUMN is_deferred boolean NOT NULL DEFAULT false; 
            END IF; 
        END$$;
    """)
    
    # 5) دالة تطبيع الحالة
    op.execute("""
        CREATE OR REPLACE FUNCTION normalize_order_status(_s text) 
        RETURNS text AS $$ 
        DECLARE 
            s text; 
        BEGIN 
            IF _s IS NULL THEN 
                RETURN 'pending'; 
            END IF; 
            s := LOWER(TRIM(_s)); 
            IF s = 'issue' THEN 
                s := 'problem'; 
            END IF;
            IF s IN ('accepted', 'waiting_restaurant_acceptance') THEN
                s := 'choose_captain';
            END IF;
            IF s IN ('preparing', 'pick_up_ready') THEN
                s := 'processing';
            END IF;
            RETURN s; 
        END$$ LANGUAGE plpgsql IMMUTABLE;
    """)
    
    # 6) Trigger BEFORE INSERT/UPDATE لتطبيع الحالة ومنع أي non-enum
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_orders_normalize_status() 
        RETURNS trigger AS $$ 
        BEGIN 
            NEW.status := normalize_order_status(NEW.status); 
            IF NEW.status NOT IN (
                'pending','choose_captain','processing','out_for_delivery','delivered','cancelled','problem'
            ) THEN 
                RAISE EXCEPTION 'Invalid status value: %', NEW.status; 
            END IF; 
            RETURN NEW; 
        END$$ LANGUAGE plpgsql;
    """)
    
    op.execute("DROP TRIGGER IF EXISTS orders_normalize_status ON orders")
    op.execute("""
        CREATE TRIGGER orders_normalize_status 
        BEFORE INSERT OR UPDATE ON orders 
        FOR EACH ROW 
        EXECUTE FUNCTION trg_orders_normalize_status();
    """)
    
    # 7) فهارس أساسية للأداء
    op.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC)")


def downgrade():
    # حذف القيود/الترغر/الفهارس فقط
    op.execute("DROP TRIGGER IF EXISTS orders_normalize_status ON orders")
    op.execute("DROP FUNCTION IF EXISTS trg_orders_normalize_status()")
    op.execute("DROP FUNCTION IF EXISTS normalize_order_status(text)")
    op.execute("DROP INDEX IF EXISTS idx_orders_status")
    op.execute("DROP INDEX IF EXISTS idx_orders_created_at")
    op.execute("ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_status_check")
    op.execute("ALTER TABLE orders ALTER COLUMN status DROP DEFAULT")
