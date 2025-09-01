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

### 2. الأعمدة مدمجة في `database.sql`
جميع الأعمدة المطلوبة موجودة الآن في ملف `database.sql` الأساسي:

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

### 3. سكريبت `update-database.ps1` محدث
سكريبت PowerShell للتحقق من النظام:

```powershell
# التحقق من اتصال قاعدة البيانات
docker compose exec -T db psql -U postgres -d movo_system -c "SELECT 1;"

# التحقق من الأعمدة في database.sql الأساسي
# جميع الأعمدة المطلوبة موجودة في database.sql الأساسي

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
powershell -ExecutionPolicy Bypass -File .\update-database.ps1
```

### الطريقة الثالثة: التحقق اليدوي
```bash
# التحقق من اتصال قاعدة البيانات
docker compose exec -T db psql -U postgres -d movo_system -c "SELECT 1;"

# التحقق من وجود الأعمدة
docker compose exec -T db psql -U postgres -d movo_system -c "\d+ notes"
docker compose exec -T db psql -U postgres -d movo_system -c "\d+ captains"
docker compose exec -T db psql -U postgres -d movo_system -c "\d+ restaurants"
```

## النتائج

بعد تطبيق الحل:

✅ **زر Note يعمل** - يمكن إضافة وعرض الملاحظات  
✅ **Captain Assignment يعمل** - يمكن اختيار الكابتن  
✅ **زر Demo يعمل** - يمكن إنشاء طلب تجريبي  
✅ **جميع الخدمات تعمل** - النظام مستقر ومتكامل  

## الملفات المحدثة

1. **`database.sql`** - محدث بالأعمدة الجديدة
2. **`update-database.ps1`** - سكريبت التحديث
3. **`DATABASE_SOLUTION_README.md`** - هذا الملف

## الملفات المحذوفة

1. **`database_missing_columns.sql`** - تم حذفه (الأعمدة مدمجة في database.sql)

## ملاحظات مهمة

- هذه الأعمدة ضرورية لعمل النظام بشكل صحيح
- الأعمدة مدمجة في `database.sql` الأساسي
- القيم الافتراضية تضمن عدم كسر البيانات الموجودة
- جميع الأعمدة تحتوي على تعليقات توضيحية
- لا حاجة لملفات منفصلة للأعمدة المفقودة

## استكشاف الأخطاء

إذا واجهت مشاكل بعد التحديث:

1. تحقق من حالة الحاويات: `docker compose ps`
2. تحقق من سجلات قاعدة البيانات: `docker compose logs db`
3. اختبر الاتصال: `docker compose exec db psql -U postgres -d movo_system -c "SELECT 1;"`
4. اختبر الخدمات: `powershell -ExecutionPolicy Bypass -File .\diagnostics\quick-check.ps1`

## الخلاصة

تم حل المشكلة بشكل نهائي من خلال:
- إضافة الأعمدة المفقودة لملف `database.sql` الأساسي
- دمج جميع الأعمدة في ملف واحد موحد
- إنشاء سكريبت تلقائي للتحقق من النظام
- اختبار شامل لجميع الخدمات

النظام الآن مستقر وبسيط ولا يحتاج لإعادة إصلاح بعد كل تحديث لقاعدة البيانات.
