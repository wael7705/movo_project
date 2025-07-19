import streamlit as st

st.set_page_config(page_title="تسجيل دخول موظف", layout="centered")

if 'employee_login_step' not in st.session_state:
    st.session_state['employee_login_step'] = 1
if 'employee_phone' not in st.session_state:
    st.session_state['employee_phone'] = ''

# --- Step 1: Login ---
def login_step():
    st.header("تسجيل الدخول للموظف")
    phone = st.text_input("رقم الجوال")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("التالي"):
        if not phone or not password:
            st.error("يرجى إدخال رقم الجوال وكلمة المرور")
            return
        st.session_state['employee_phone'] = phone
        st.session_state['employee_login_step'] = 2

# --- Step 2: OTP ---
def otp_step():
    st.header("التحقق برمز OTP")
    st.info(f"تم إرسال رمز التحقق إلى رقم الجوال: {st.session_state['employee_phone']}")
    otp = st.text_input("رمز التحقق (OTP)")
    if st.button("تأكيد/التالي"):
        # لا تحقق حقيقي، فقط انتقال
        st.session_state['employee_login_step'] = 3

# --- Step 3: Welcome/Dashboard ---
def welcome_step():
    st.success("تم تسجيل الدخول بنجاح!")
    st.header("مرحباً بك في لوحة تحكم الموظف")
    st.write(f"رقم الجوال: {st.session_state['employee_phone']}")
    st.write("هنا يمكنك إدارة الطلبات، متابعة المشاكل، والمزيد...")
    if st.button("تسجيل خروج"):
        st.session_state['employee_login_step'] = 1
        st.session_state['employee_phone'] = ''

# --- Main Flow ---
if st.session_state['employee_login_step'] == 1:
    login_step()
elif st.session_state['employee_login_step'] == 2:
    otp_step()
elif st.session_state['employee_login_step'] == 3:
    welcome_step() 