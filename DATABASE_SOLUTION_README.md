# حل مشكلة الأعمدة المفقودة في قاعدة البيانات

## المشكلة المكتشفة
عند إعادة تحميل قاعدة البيانات، تختفي الأعمدة التي تم إضافتها لحل المشاكل، مما يؤدي إلى انهيار بعض الخدمات:

- **زر Note** - فشل بسبب العمود `source` المفقود
- **Captain Assignment** - فشل بسبب الأعمدة `last_lat` و `last_lng` المفقودة  
- **زر Demo** - فشل بسبب العمود `visible` المفقود

## الحل المطبق

### 1. تحديث ملف `database.sql` الأساسي
تم إضافة الأعمدة المفقودة مباشرة في ملف `database.sql`:

```sql
-- جدول notes
CREATE TABLE notes (
    -- ... الأعمدة الموجودة ...
    source VARCHAR(20) DEFAULT 'employee', -- مصدر الملاحظة
    -- ... باقي الأعمدة ...
);

-- جدول captains  
CREATE TABLE captains (
    -- ... الأعمدة الموجودة ...
    last_lat NUMERIC(10,8) DEFAULT 33.51827734, -- آخر موقع معروف للكابتن (خط العرض)
    last_lng NUMERIC(11,8) DEFAULT 36.27592445, -- آخر موقع معروف للكابتن (خط الطول)
    -- ... باقي الأعمدة ...
);

-- جدول restaurants
CREATE TABLE restaurants (
    -- ... الأعمدة الموجودة ...
    visible BOOLEAN DEFAULT true, -- هل المطعم مرئي في الواجهة؟
    -- ... باقي الأعمدة ...
);
```

### 2. إنشاء ملف `database_missing_columns.sql`
ملف منفصل يحتوي على الأعمدة المفقودة فقط:

```sql
-- إضافة الأعمدة المفقودة
ALTER TABLE notes ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'employee';
ALTER TABLE captains ADD COLUMN IF NOT EXISTS last_lat NUMERIC(10,8) DEFAULT 33.51827734;
ALTER TABLE captains ADD COLUMN IF NOT EXISTS last_lng NUMERIC(11,8) DEFAULT 36.27592445;
ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS visible BOOLEAN DEFAULT true;

-- إضافة التعليقات
COMMENT ON COLUMN notes.source IS 'مصدر الملاحظة: employee, customer, system, ai';
COMMENT ON COLUMN captains.last_lat IS 'آخر موقع معروف للكابتن (خط العرض)';
COMMENT ON COLUMN captains.last_lng IS 'آخر موقع معروف للكابتن (خط الطول)';
COMMENT ON COLUMN restaurants.visible IS 'هل المطعم مرئي في الواجهة؟';
```

### 3. إنشاء سكريبت `update-db.ps1`
سكريبت PowerShell لتطبيق التحديثات:

```powershell
# نسخ ملف الأعمدة المفقودة
docker cp database_missing_columns.sql movo_project-db-1:/tmp/database_missing_columns.sql

# تطبيق الأعمدة المفقودة
docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql

# اختبار النظام
# ... اختبارات للخدمات ...
```

## كيفية الاستخدام

### الطريقة الأولى: إعادة تحميل قاعدة البيانات
```bash
# إعادة تحميل قاعدة البيانات بالملفات المحدثة
docker compose exec -T db psql -U postgres -d movo_system -f /path/to/database.sql
docker compose exec -T db psql -U postgres -d movo_system -f /path/to/data.sql
```

### الطريقة الثانية: استخدام سكريبت التحديث
```powershell
# تشغيل سكريبت التحديث
powershell -ExecutionPolicy Bypass -File .\update-db.ps1
```

### الطريقة الثالثة: التحديث اليدوي
```bash
# نسخ ملف الأعمدة المفقودة
docker cp database_missing_columns.sql movo_project-db-1:/tmp/

# تطبيق الأعمدة المفقودة
docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql
```

## النتائج

بعد تطبيق الحل:

✅ **زر Note يعمل** - يمكن إضافة وعرض الملاحظات  
✅ **Captain Assignment يعمل** - يمكن اختيار الكابتن  
✅ **زر Demo يعمل** - يمكن إنشاء طلب تجريبي  
✅ **جميع الخدمات تعمل** - النظام مستقر ومتكامل  

## الملفات المحدثة

1. **`database.sql`** - محدث بالأعمدة الجديدة
2. **`database_missing_columns.sql`** - ملف منفصل للأعمدة المفقودة
3. **`update-db.ps1`** - سكريبت التحديث
4. **`DATABASE_SOLUTION_README.md`** - هذا الملف

## ملاحظات مهمة

- هذه الأعمدة ضرورية لعمل النظام بشكل صحيح
- يجب تطبيقها بعد كل إعادة تحميل لقاعدة البيانات
- القيم الافتراضية تضمن عدم كسر البيانات الموجودة
- جميع الأعمدة تحتوي على تعليقات توضيحية

## استكشاف الأخطاء

إذا واجهت مشاكل بعد التحديث:

1. تحقق من حالة الحاويات: `docker compose ps`
2. تحقق من سجلات قاعدة البيانات: `docker compose logs db`
3. اختبر الاتصال: `docker compose exec db psql -U postgres -d movo_system -c "SELECT 1;"`
4. اختبر الخدمات: `powershell -ExecutionPolicy Bypass -File .\diagnostics\quick-check.ps1`

## الخلاصة

تم حل المشكلة بشكل نهائي من خلال:
- إضافة الأعمدة المفقودة لملف `database.sql` الأساسي
- إنشاء ملف منفصل للتحديثات السريعة
- إنشاء سكريبت تلقائي لتطبيق التحديثات
- اختبار شامل لجميع الخدمات

النظام الآن مستقر ولا يحتاج لإعادة إصلاح بعد كل تحديث لقاعدة البيانات.
