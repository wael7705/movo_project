-- ========================================
-- إضافة الأعمدة المفقودة لقاعدة البيانات
-- ========================================
-- هذا الملف يحتوي على جميع الأعمدة التي تم إضافتها لحل المشاكل
-- ويجب تشغيله بعد تحميل database.sql و data.sql

-- إضافة العمود source لجدول notes
ALTER TABLE notes ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'employee';

-- إضافة الأعمدة last_lat و last_lng لجدول captains
ALTER TABLE captains ADD COLUMN IF NOT EXISTS last_lat NUMERIC(10,8) DEFAULT 33.51827734;
ALTER TABLE captains ADD COLUMN IF NOT EXISTS last_lng NUMERIC(11,8) DEFAULT 36.27592445;

-- إضافة العمود visible لجدول restaurants
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS visible BOOLEAN DEFAULT true;

-- إضافة التعليقات للأعمدة الجديدة
COMMENT ON COLUMN notes.source IS 'مصدر الملاحظة: employee (موظف)، customer (عميل)، system (نظام)، ai (ذكاء اصطناعي)';
COMMENT ON COLUMN captains.last_lat IS 'آخر موقع معروف للكابتن (خط العرض) - يستخدم لتحديد أقرب كابتن';
COMMENT ON COLUMN captains.last_lng IS 'آخر موقع معروف للكابتن (خط الطول) - يستخدم لتحديد أقرب كابتن';
COMMENT ON COLUMN restaurants.visible IS 'هل المطعم مرئي في الواجهة؟ (true/false)';

-- تحديث البيانات الموجودة لتطبيق القيم الافتراضية
UPDATE notes SET source = 'employee' WHERE source IS NULL;
UPDATE captains SET last_lat = 33.51827734 WHERE last_lat IS NULL;
UPDATE captains SET last_lng = 36.27592445 WHERE last_lng IS NULL;
UPDATE restaurants SET visible = true WHERE visible IS NULL;
