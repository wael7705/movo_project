# MOVO Project - نظام توثيق وصلاحيات احترافي

- النظام الآن يدعم تسجيل دخول وتوثيق JWT وصلاحيات مرنة باستخدام fastapi-users.
- يوجد جدول users أساسي مرتبط بجداول العملاء والكباتن والمطاعم.
- كل التعديلات موثقة وسيتم توفير تقرير مفصل لاحقًا.

---

# 🚀 MOVO Delivery Platform

## 🎯 نظرة سريعة

نظام MOVO للتوصيل - منصة شاملة لإدارة عمليات التوصيل مع دعم الذكاء الاصطناعي.

## ⚡ التشغيل السريع

```bash
# الطريقة الأسهل
python quick_start.py

# الطريقة البديلة
python start.py

# الطريقة المباشرة
python app.py
```

## 📚 التوثيق

- `README_NEW.md` - دليل شامل مفصل
- `DEPLOYMENT.md` - دليل النشر للإنتاج
- `CLEANUP.md` - تفاصيل التنظيف
- `CHANGELOG.md` - سجل التغييرات

## 🧪 الاختبار

```bash
# اختبار شامل
python FINAL_TEST.py

# اختبار سريع
python test_new_system.py
```

## 🎉 النظام جاهز!

**✅ منظم ومحسن**  
**✅ جاهز للذكاء الاصطناعي**  
**✅ جاهز للواجهة الجديدة**  
**✅ جاهز للإنتاج** 

---

## Tech Stack & Auth System

- FastAPI (backend framework)
- fastapi-users (authentication & user management)
- SQLAlchemy (ORM)
- asyncpg (PostgreSQL async driver)
- Streamlit (dashboard/frontend)
- JWT (JSON Web Token for secure auth)
- passlib (password hashing)
- python-jose (JWT implementation)
- Alembic (migrations)
- geopy, folium, streamlit-folium (geo/maps)
- كل التعديلات موثقة وسيتم توفير تقرير مفصل لاحقًا حسب طلب العميل. 

## FastAPI Async Migration (ملخص)

- FastAPI 0.110 مع Uvicorn.
- SQLAlchemy 2.0 async مع `asyncpg` واعتمادية `get_db` غير المتزامنة.
- Pydantic v2 في `backend/schemas/`.
- Alembic async مهيأ في `alembic/` و`alembic.ini`.
- مسار عام بدون مصادقة: `/orders` يعيد `OrderCard[]`.
- اختبارات `pytest-asyncio` ضمن `tests/`.

## تسجيل مستخدم جديد (عميل) مع OTP وعنوان

1. أرسل رقم الهاتف إلى `/auth/send_otp` لاستقبال رمز التحقق (OTP)
2. تحقق من الرمز عبر `/auth/verify_otp`
3. بعد التحقق، استخدم `/auth/register_by_phone` لإنشاء المستخدم (role=customer)
4. أرسل بيانات العميل إلى `/customers/with_user` لربطه بجدول العملاء
5. أضف عنوان عبر `/customers/address` (مع دعم Autocomplete في الواجهة)

### مثال عبر Postman:
- إرسال OTP:
  ```json
  POST /auth/send_otp
  { "phone": "09xxxxxxxx" }
  ```
- تحقق OTP:
  ```json
  POST /auth/verify_otp
  { "phone": "09xxxxxxxx", "otp": "123456" }
  ```
- تسجيل مستخدم:
  ```json
  POST /auth/register_by_phone
  { "phone": "09xxxxxxxx", "password": "yourpass", "role": "customer" }
  ```
- ربط بيانات العميل:
  ```json
  POST /customers/with_user
  { "name": "اسم العميل", "phone": "09xxxxxxxx", "latitude": 33.5, "longitude": 36.3, "user_id": 1 }
  ```
- إضافة عنوان:
  ```json
  POST /customers/address
  { "customer_id": 1, "city": "دمشق", "street": "شارع الثورة", "latitude": 33.5, "longitude": 36.3 }
  ```

## Autocomplete للعناوين
- الواجهة الأمامية (Streamlit) تدعم اقتراح العناوين تلقائياً عبر Google Places أو Nominatim.

## لتجريب الواجهة:
- شغل backend ثم شغل ملف Streamlit الخاص بالتسجيل (سيتم توفيره) 