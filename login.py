import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="تسجيل الدخول", layout="centered")
st.title("تسجيل الدخول إلى النظام")

if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None

# --- Login Form ---
with st.form("login_form"):
    phone = st.text_input("رقم الجوال")
    password = st.text_input("كلمة المرور", type="password")
    submitted = st.form_submit_button("تسجيل الدخول")

if submitted:
    payload_username = {"username": phone, "password": password}
    payload_phone = {"phone": phone, "password": password}
    # جرب أولاً username، إذا فشل جرب phone
    resp = requests.post(f"{BACKEND_URL}/auth/login_by_phone/jwt/login", data=payload_username)
    data = resp.json() if resp.content else {}
    if resp.status_code == 200 and "access_token" in data:
        token = data["access_token"]
    else:
        # جرب phone بدلاً من username
        resp2 = requests.post(f"{BACKEND_URL}/auth/login_by_phone/jwt/login", data=payload_phone)
        data2 = resp2.json() if resp2.content else {}
        if resp2.status_code == 200 and "access_token" in data2:
            token = data2["access_token"]
        else:
            st.error("بيانات الدخول غير صحيحة أو الحساب غير مفعل. (تأكد من صحة رقم الجوال وكلمة المرور)")
            token = None
    if token:
        st.session_state['token'] = token
        st.success("تم تسجيل الدخول بنجاح!")
        # Get user info
        headers = {"Authorization": f"Bearer {token}"}
        user_resp = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
        if user_resp.status_code == 200:
            user = user_resp.json()
            st.session_state['user'] = user
            st.session_state['role'] = user.get('role')
        else:
            st.error(f"فشل في جلب بيانات المستخدم. (الكود: {user_resp.status_code})")
    # else تمت معالجة الخطأ أعلاه

# --- Dashboard by Role ---
if st.session_state['user']:
    st.header(f"مرحباً {st.session_state['user']['phone']}!")
    role = st.session_state['role']
    if role == 'customer':
        st.success("لوحة تحكم العميل: يمكنك الآن تصفح الطلبات أو تعديل بياناتك.")
    elif role == 'captain':
        st.info("لوحة تحكم الكابتن: يمكنك استلام الطلبات ومتابعة التوصيل.")
    elif role == 'restaurant':
        st.info("لوحة تحكم المطعم: يمكنك إدارة الطلبات وقائمة الطعام.")
    elif role == 'admin':
        st.warning("لوحة تحكم المدير: صلاحيات كاملة على النظام.")
    elif role == 'call_center_agent':
        st.info("لوحة تحكم موظف الكول سنتر: إدارة ومتابعة مشاكل العملاء.")
    elif role == 'call_center_supervisor':
        st.info("لوحة تحكم مشرف الكول سنتر: إشراف وتحليل أداء الفريق.")
    elif role == 'data_entry':
        st.info("لوحة تحكم موظف الداتا: إدخال وتحديث البيانات.")
    elif role == 'ai':
        st.info("لوحة تحكم الذكاء الاصطناعي: مراقبة وتحليل النظام.")
    else:
        st.info(f"لوحة تحكم الدور: {role}")
    if st.button("تسجيل الخروج"):
        st.session_state['token'] = None
        st.session_state['user'] = None
        st.session_state['role'] = None
        st.rerun() 