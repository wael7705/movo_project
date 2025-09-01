# تحديث قاعدة البيانات - إضافة الأعمدة المفقودة

## المشكلة
عند إعادة تحميل قاعدة البيانات، تختفي الأعمدة التي تم إضافتها لحل المشاكل، مما يؤدي إلى انهيار بعض الخدمات.

## الحل
تم إنشاء ملفات محدثة تحتوي على جميع الأعمدة المفقودة:

### الملفات المحدثة:

1. **`database.sql`** - الملف الأساسي محدث بالأعمدة الجديدة:
   - `notes.source` - مصدر الملاحظة
   - `captains.last_lat` - آخر موقع معروف للكابتن (خط العرض)
   - `captains.last_lng` - آخر موقع معروف للكابتن (خط الطول)
   - `restaurants.visible` - هل المطعم مرئي في الواجهة

2. **`database_missing_columns.sql`** - ملف منفصل يحتوي على الأعمدة المفقودة فقط

3. **`update-database.ps1`** - سكريبت PowerShell لتطبيق التحديثات

## كيفية الاستخدام:

### الطريقة الأولى: استخدام الملفات المحدثة
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

### الطريقة الثالثة: التحديث اليدوي
```bash
# نسخ ملف الأعمدة المفقودة
docker cp database_missing_columns.sql movo_project-db-1:/tmp/

# تطبيق الأعمدة المفقودة
docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql
```

## الأعمدة المضافة:

### جدول `notes`:
- **`source`** VARCHAR(20) DEFAULT 'employee'
  - مصدر الملاحظة: employee, customer, system, ai

### جدول `captains`:
- **`last_lat`** NUMERIC(10,8) DEFAULT 33.51827734
  - آخر موقع معروف للكابتن (خط العرض)
- **`last_lng`** NUMERIC(11,8) DEFAULT 36.27592445
  - آخر موقع معروف للكابتن (خط الطول)

### جدول `restaurants`:
- **`visible`** BOOLEAN DEFAULT true
  - هل المطعم مرئي في الواجهة

## التحقق من التحديث:

بعد تطبيق التحديثات، تأكد من عمل الخدمات التالية:

1. **زر Note** - إضافة وعرض الملاحظات
2. **Captain Assignment** - اختيار الكابتن
3. **زر Demo** - إنشاء طلب تجريبي

## ملاحظات مهمة:

- هذه الأعمدة ضرورية لعمل النظام بشكل صحيح
- يجب تطبيقها بعد كل إعادة تحميل لقاعدة البيانات
- القيم الافتراضية تضمن عدم كسر البيانات الموجودة
- جميع الأعمدة تحتوي على تعليقات توضيحية

## استكشاف الأخطاء:

إذا واجهت مشاكل بعد التحديث:

1. تحقق من حالة الحاويات: `docker compose ps`
2. تحقق من سجلات قاعدة البيانات: `docker compose logs db`
3. اختبر الاتصال: `docker compose exec db psql -U postgres -d movo_system -c "SELECT 1;"`
4. اختبر الخدمات: `powershell -ExecutionPolicy Bypass -File .\diagnostics\quick-check.ps1`
