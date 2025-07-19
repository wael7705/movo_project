# 🚀 MOVO Quick Guide - دليل سريع

## ⚡ التشغيل السريع

### 1. تفعيل البيئة الافتراضية
```bash
# في PowerShell
.venv\Scripts\activate

# يجب أن ترى (.venv) في بداية السطر
(.venv) PS C:\Users\waeln\project\MOVO\backend>
```

### 2. تثبيت المكتبات (إذا لم تكن مثبتة)
```bash
pip install -r requirements.txt
```

### 3. تشغيل النظام
```bash
# الطريقة الأسهل
python start_simple.py

# الطريقة البديلة
python app.py

# الطريقة المباشرة
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 الاختبار

### اختبار بسيط
```bash
python test_simple.py
```

### اختبار شامل
```bash
python test_new_system.py
```

## 🔧 حل المشاكل

### مشكلة: "ModuleNotFoundError"
**الحل:** تأكد من تفعيل البيئة الافتراضية
```bash
.venv\Scripts\activate
```

### مشكلة: "ImportError"
**الحل:** أعد تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### مشكلة: "Database connection error"
**الحل:** تأكد من تشغيل PostgreSQL

### مشكلة: "Port already in use"
**الحل:** غير المنفذ في `config.py`
```python
port: int = 8001  # بدلاً من 8000
```

## 📁 الملفات المهمة

- `start_simple.py` - تشغيل سريع
- `app.py` - التطبيق الرئيسي
- `config.py` - الإعدادات
- `database.py` - قاعدة البيانات
- `services.py` - الخدمات

## 🌐 الوصول للتطبيق

بعد التشغيل، اذهب إلى:
- **التطبيق:** http://localhost:8000
- **التوثيق:** http://localhost:8000/docs
- **الاختبار:** http://localhost:8000/health

## 🎯 النقاط المهمة

1. **يجب تفعيل البيئة الافتراضية دائماً**
2. **استخدم `start_simple.py` للتشغيل السريع**
3. **تحقق من تشغيل PostgreSQL**
4. **راجع السجلات للأخطاء**

---

**🎉 النظام جاهز للعمل!** 

## خطوات تسجيل مستخدم جديد (عميل) مع OTP وعنوان:
1. إرسال رقم الهاتف إلى `/auth/send_otp`
2. تحقق من الرمز عبر `/auth/verify_otp`
3. تسجيل مستخدم عبر `/auth/register_by_phone`
4. ربط بيانات العميل عبر `/customers/with_user`
5. إضافة عنوان عبر `/customers/address`

## Autocomplete للعناوين:
- استخدم واجهة Streamlit الجديدة لتجربة ميزة الاقتراح التلقائي للعناوين. 