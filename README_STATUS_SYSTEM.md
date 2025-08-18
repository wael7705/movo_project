# نظام الحالات الجديد - دليل الاستخدام

## نظرة عامة

تم تحديث نظام الحالات في تطبيق Movo ليعمل بنظام موحد ومتسق. كل طلب يظهر في تبويب واحد فقط، مع إمكانية تتبع التقدم عبر الحالات المختلفة.

## الحالات المتاحة

### 1. **قيد الانتظار** (`pending`)
- الطلبات الجديدة التي تم إنشاؤها
- تنتظر معالجة من قبل المطعم

### 2. **تعيين كابتن** (`choose_captain`)
- الطلبات التي تم قبولها من المطعم
- تنتظر تعيين كابتن للتوصيل

### 3. **معالجة** (`processing`)
- الطلبات قيد التحضير في المطعم
- تنقسم إلى ثلاث مراحل فرعية:
  - **انتظار الموافقة**: الطلب مقبول ويتم التحضير
  - **التحضير**: الطلب قيد التحضير
  - **الكابتن استلم**: الطلب جاهز للاستلام من الكابتن

### 4. **خرج للتوصيل** (`out_for_delivery`)
- الطلب في الطريق للعميل

### 5. **تم التوصيل** (`delivered`)
- الطلب تم توصيله بنجاح

### 6. **ملغي** (`cancelled`)
- الطلب تم إلغاؤه

### 7. **مشكلة** (`problem`)
- الطلب يواجه مشكلة تحتاج حل

## كيفية الاستخدام

### إنشاء طلبات وهمية

#### 1. من الواجهة الأمامية
- استخدم زر **"إنشاء طلب وهمي"** لإنشاء طلب في حالة `pending`
- استخدم زر **"إنشاء طلب معالج"** لإنشاء طلب في حالة `processing`

#### 2. من قاعدة البيانات
```bash
# استيراد البيانات الوهمية الأساسية
python import_fake_data.py

# أو إنشاء طلبات وهمية إضافية
python create_demo_orders.py

# أو إنشاء بيانات وهمية كاملة
python generate_fake_data.py
```

### تقدم الطلبات

#### من `pending` إلى `choose_captain`
- اضغط على زر **"التالي"** في الطلب

#### من `choose_captain` إلى `processing`
- اضغط على زر **"تعيين"** في الطلب

#### داخل `processing` (المراحل الفرعية)
- **انتظار الموافقة** → **التحضير** → **الكابتن استلم**
- اضغط على زر **"التالي"** للانتقال بين المراحل

#### من `processing` إلى `out_for_delivery`
- عندما يصل الطلب لمرحلة "الكابتن استلم"
- اضغط على زر **"التالي"** للانتقال

#### من `out_for_delivery` إلى `delivered`
- اضغط على زر **"التالي"** عند اكتمال التوصيل

### إلغاء الطلبات
- استخدم زر **"إلغاء"** في أي مرحلة
- سيتم نقل الطلب إلى تبويب **"ملغي"**

### الإبلاغ عن المشاكل
- استخدم زر **"مشكلة"** في أي مرحلة
- سيتم نقل الطلب إلى تبويب **"مشكلة"**

## الملفات المحدثة

### Backend
- `backend/core/status.py` - نظام الحالات الموحد
- `backend/core/constants.py` - ثوابت الحالات
- `backend/api/routes/orders.py` - API الطلبات
- `backend/models/order.py` - نموذج الطلب

### Frontend
- `movo-ts/src/pages/Dashboard.tsx` - الواجهة الرئيسية
- `movo-ts/src/components/OrderCard.tsx` - بطاقة الطلب
- `movo-ts/src/services/ordersApi.ts` - خدمة API الطلبات

### Scripts
- `import_fake_data.py` - استيراد البيانات الوهمية الأساسية
- `create_demo_orders.py` - إنشاء طلبات وهمية إضافية
- `generate_fake_data.py` - إنشاء بيانات وهمية كاملة
- `fake_data.sql` - ملف SQL يحتوي على البيانات الوهمية
- `fix_processing_substages.py` - إصلاح substages الطلبات
- `check_processing_orders.py` - فحص الطلبات في حالة processing

## تشغيل النظام

### 1. تشغيل Backend
```bash
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 2. تشغيل Frontend
```bash
cd movo-ts
pnpm install
pnpm dev
```

### 3. استيراد البيانات الوهمية
```bash
# أولاً: استيراد البيانات الأساسية
python import_fake_data.py

# ثم: إنشاء طلبات إضافية (اختياري)
python create_demo_orders.py
```

## حل مشكلة "No customer/restaurant available"

إذا واجهت هذا الخطأ، فهذا يعني أن قاعدة البيانات فارغة من العملاء والمطاعم. إليك الحل:

### الحل السريع:
```bash
# 1. تأكد من تشغيل قاعدة البيانات PostgreSQL
# 2. شغل ملف استيراد البيانات
python import_fake_data.py
```

### الحل التفصيلي:
1. **تأكد من قاعدة البيانات**:
   ```bash
   psql -U postgres -d movo_system -c "SELECT COUNT(*) FROM customers;"
   psql -U postgres -d movo_system -c "SELECT COUNT(*) FROM restaurants;"
   ```

2. **إذا كانت فارغة، استورد البيانات**:
   ```bash
   python import_fake_data.py
   ```

3. **تحقق من البيانات**:
   ```bash
   psql -U postgres -d movo_system -c "SELECT name FROM customers LIMIT 5;"
   psql -U postgres -d movo_system -c "SELECT name FROM restaurants LIMIT 5;"
   ```

### إذا فشل الاستيراد:
1. **تحقق من الاتصال**:
   - تأكد من تشغيل PostgreSQL
   - تحقق من بيانات الاتصال في `DB_CONFIG`

2. **تحقق من الجداول**:
   ```bash
   psql -U postgres -d movo_system -c "\dt"
   ```

3. **شغل migration**:
   ```bash
   python run_migration.py
   ```

## حل مشكلة عدم ظهور الطلبات في أعمدة processing

إذا كانت الطلبات لا تظهر في الأعمدة الثلاثة لتبويب `processing`، فهذا يعني أن هناك مشكلة في `substage` أو `current_stage_name`. إليك الحل:

### الحل السريع:
```bash
# إصلاح substages الطلبات في حالة processing
python fix_processing_substages.py
```

### الحل التفصيلي:
1. **فحص الطلبات الحالية**:
   ```bash
   python check_processing_orders.py
   ```

2. **إصلاح substages**:
   ```bash
   python fix_processing_substages.py
   ```

3. **التحقق من الإصلاح**:
   ```bash
   python check_processing_orders.py --check
   ```

### ما يتم إصلاحه:
- تحديث الطلبات التي ليس لها `current_stage_name`
- تحديث الطلبات التي لها `current_stage_name` قديم
- إضافة طلبات تجريبية في حالات مختلفة إذا لم تكن موجودة
- ضمان وجود طلبات في كل من الأعمدة الثلاثة

### الأعمدة المطلوبة:
1. **انتظار الموافقة** (`waiting_approval`)
2. **التحضير** (`preparing`)
3. **الكابتن استلم** (`captain_received`)

## استكشاف الأخطاء

### مشكلة: لا تظهر الطلبات
1. تأكد من تشغيل Backend
2. تحقق من قاعدة البيانات
3. افحص console المتصفح للأخطاء
4. **تأكد من وجود بيانات في قاعدة البيانات**

### مشكلة: "No customer/restaurant available"
1. **استورد البيانات الوهمية**: `python import_fake_data.py`
2. تحقق من وجود العملاء والمطاعم
3. تأكد من صحة الاتصال بقاعدة البيانات

### مشكلة: لا تظهر الطلبات في أعمدة processing
1. **أصلح substages**: `python fix_processing_substages.py`
2. تحقق من وجود طلبات في حالة `processing`
3. تأكد من أن كل طلب له `current_stage_name` صحيح
4. تحقق من أن `substage` يتم حسابه بشكل صحيح

### مشكلة: لا تعمل أزرار التقدم
1. تأكد من صحة API endpoints
2. تحقق من قاعدة البيانات
3. افحص logs الـ Backend

### مشكلة: الطلبات تظهر في تبويبات خاطئة
1. تأكد من تحديث قاعدة البيانات
2. تحقق من نظام الحالات
3. افحص migration files

## API Endpoints

### إنشاء طلب وهمي
```http
POST /api/v1/orders/demo
```

### إنشاء طلب معالج
```http
POST /api/v1/orders/demo/processing
```

### تقدم الطلب
```http
PATCH /api/v1/orders/{id}/next
```

### إلغاء الطلب
```http
PATCH /api/v1/orders/{id}/cancel
```

### قائمة الطلبات
```http
GET /api/v1/orders?order_status={status}
```

## ملاحظات مهمة

1. **نظام الحالات الموحد**: كل طلب يظهر في تبويب واحد فقط
2. **المراحل الفرعية**: تبويب المعالجة يحتوي على ثلاث مراحل
3. **التقدم التلقائي**: يمكن تقدم الطلبات عبر الأزرار
4. **البيانات الوهمية**: يمكن إنشاؤها من الواجهة أو قاعدة البيانات
5. **التوافق**: النظام متوافق مع البيانات الموجودة
6. **البيانات الأساسية**: تأكد من وجود عملاء ومطاعم قبل إنشاء الطلبات
7. **substages**: تأكد من أن الطلبات في حالة `processing` لها `current_stage_name` صحيح

## الدعم

إذا واجهت أي مشاكل، يرجى:
1. فحص logs النظام
2. التأكد من تحديث جميع الملفات
3. التحقق من قاعدة البيانات
4. **استيراد البيانات الوهمية**: `python import_fake_data.py`
5. **إصلاح substages**: `python fix_processing_substages.py`
6. مراجعة هذا الدليل

## تسلسل التشغيل الموصى به

```bash
# 1. تشغيل قاعدة البيانات PostgreSQL
# 2. تشغيل Backend
cd backend
python -m uvicorn app:app --reload

# 3. في terminal آخر: استيراد البيانات
python import_fake_data.py

# 4. إصلاح substages (إذا لزم الأمر)
python fix_processing_substages.py

# 5. تشغيل Frontend
cd movo-ts
pnpm dev

# 6. اختبار النظام
# افتح المتصفح على http://localhost:5173
# تأكد من ظهور الطلبات في أعمدة processing
```
