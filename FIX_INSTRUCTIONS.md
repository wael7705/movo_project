# تعليمات إصلاح مشكلة العمود المفقود

## المشكلة:
الكود يحاول الوصول إلى عمود `visible` في جدول `restaurants`، لكن هذا العمود غير موجود في قاعدة البيانات.

## الحل:

### 1. إضافة العمود المفقود:
```sql
-- إضافة العمود المفقود visible إلى جدول restaurants
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS visible BOOLEAN DEFAULT true;

-- تحديث البيانات الموجودة
UPDATE restaurants SET visible = true WHERE visible IS NULL;

-- إضافة فهرس للعمود الجديد
CREATE INDEX IF NOT EXISTS idx_restaurants_visible ON restaurants(visible);
```

### 2. تنفيذ الإصلاح:

#### الطريقة الأولى: عبر Docker Compose
```bash
# تشغيل المشروع
docker compose up -d

# الدخول إلى قاعدة البيانات
docker compose exec db psql -U postgres -d movo_system

# تنفيذ الأوامر SQL أعلاه
```

#### الطريقة الثانية: عبر pgAdmin
1. افتح pgAdmin
2. اتصل بقاعدة البيانات:
   - Host: localhost
   - Port: 6432 (عبر pgbouncer) أو 5432 (مباشر)
   - User: postgres
   - Password: movo2025
   - Database: movo_system
3. نفذ الأوامر SQL أعلاه

### 3. إعادة تشغيل التطبيق:
```bash
docker compose restart app
```

## سبب المشكلة:
- النموذج `backend/models/restaurant.py` يحتوي على عمود `visible`
- لكن قاعدة البيانات لا تحتويه
- هذا يسبب خطأ `UndefinedColumnError`

## بعد الإصلاح:
- زر "Demo" سيعمل
- تبويب "تعيين كابتن" سيعمل
- جميع الطلبات ستظهر بشكل صحيح
