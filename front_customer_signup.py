import streamlit as st
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium

st.set_page_config(page_title="تسجيل عميل جديد", layout="centered")

if 'customer_signup_step' not in st.session_state:
    st.session_state['customer_signup_step'] = 1
if 'customer_signup_data' not in st.session_state:
    st.session_state['customer_signup_data'] = {}

# --- Step 1: Basic Info ---
def step1():
    st.header("البيانات الأساسية")
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الجوال")
    password = st.text_input("كلمة المرور", type="password")
    password2 = st.text_input("تأكيد كلمة المرور", type="password")
    if st.button("التالي"):
        if not name or not phone or not password or not password2:
            st.error("يرجى تعبئة جميع الحقول")
            return
        if password != password2:
            st.error("كلمتا المرور غير متطابقتين")
            return
        st.session_state['customer_signup_data'] = {
            'name': name,
            'phone': phone,
            'password': password
        }
        st.session_state['customer_signup_step'] = 2

# --- Step 2: OTP ---
def step2():
    st.header("التحقق من رقم الجوال")
    st.info(f"تم إرسال رمز التحقق إلى رقم الجوال: {st.session_state['customer_signup_data']['phone']}")
    otp = st.text_input("رمز التحقق (OTP)")
    if st.button("تأكيد/التالي"):
        # لا تحقق حقيقي، فقط انتقال
        st.session_state['customer_signup_step'] = 3

# --- Step 3: تحديد الموقع ---
def step3():
    st.header("تحديد الموقع والعنوان")
    address_query = st.text_input("بحث عن عنوان (Autocomplete)")
    address_suggestions = []
    if address_query:
        geolocator = Nominatim(user_agent="movo_signup")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        try:
            locations = geolocator.geocode(address_query, exactly_one=False, limit=5, **{"addressdetails": True, "language": "ar"})
        except Exception:
            locations = None
        if locations:
            if not isinstance(locations, list):
                locations = [locations]
            address_suggestions = [getattr(loc, 'address', None) for loc in locations if hasattr(loc, 'address')]
    selected = None
    if address_suggestions:
        selected = st.selectbox("اختر عنواناً مقترحاً", address_suggestions)
    st.write("حدد موقعك على الخريطة:")
    default_location = [33.5138, 36.2765]
    m = folium.Map(location=default_location, zoom_start=12)
    marker = folium.Marker(location=default_location, draggable=True)
    marker.add_to(m)
    map_data = st_folium(m, width=700, height=400)
    lat, lon = None, None
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
    if st.button("حفظ وإنهاء التسجيل"):
        st.session_state['customer_signup_data']['address'] = selected
        st.session_state['customer_signup_data']['lat'] = lat or default_location[0]
        st.session_state['customer_signup_data']['lon'] = lon or default_location[1]
        st.session_state['customer_signup_step'] = 4

# --- Step 4: Success ---
def step4():
    st.success("تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.")
    st.balloons()
    st.write("بياناتك:")
    st.json(st.session_state['customer_signup_data'])
    if st.button("العودة لتسجيل الدخول"):
        st.session_state['customer_signup_step'] = 1
        st.session_state['customer_signup_data'] = {}

# --- Main Flow ---
if st.session_state['customer_signup_step'] == 1:
    step1()
elif st.session_state['customer_signup_step'] == 2:
    step2()
elif st.session_state['customer_signup_step'] == 3:
    step3()
elif st.session_state['customer_signup_step'] == 4:
    step4() 