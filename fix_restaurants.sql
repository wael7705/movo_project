-- إضافة العمود المفقود visible إلى جدول restaurants
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS visible BOOLEAN DEFAULT true;

-- تحديث البيانات الموجودة
UPDATE restaurants SET visible = true WHERE visible IS NULL;

-- إضافة فهرس للعمود الجديد
CREATE INDEX IF NOT EXISTS idx_restaurants_visible ON restaurants(visible);
