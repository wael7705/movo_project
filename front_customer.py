import streamlit as st
import requests
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit_geolocation import streamlit_geolocation

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="تسجيل دخول عميل", layout="centered")

if 'customer_page' not in st.session_state:
    st.session_state['customer_page'] = 'login'  # 'login' or 'signup'
if 'customer_login_step' not in st.session_state:
    st.session_state['customer_login_step'] = 1
if 'customer_signup_step' not in st.session_state:
    st.session_state['customer_signup_step'] = 1
if 'customer_signup_data' not in st.session_state:
    st.session_state['customer_signup_data'] = {}
if 'customer_phone' not in st.session_state:
    st.session_state['customer_phone'] = ''
if 'customer_location' not in st.session_state:
    st.session_state['customer_location'] = {'lat': 33.5138, 'lon': 36.2765}
if 'customer_address_fields' not in st.session_state:
    st.session_state['customer_address_fields'] = {
        'city': '', 'street': '', 'district': '', 'neighborhood': '', 'additional_details': ''
    }

# --- Login Page ---
def login_page():
    st.header("تسجيل الدخول")
    phone = st.text_input("رقم الجوال", key="login_phone")
    password = st.text_input("كلمة المرور", type="password", key="login_password")
    if st.button("تسجيل الدخول"):
        if not phone or not password:
            st.error("يرجى إدخال رقم الجوال وكلمة المرور")
            return
        st.success("تم تسجيل الدخول (وهمياً)")
        st.session_state['customer_login_step'] = 3
        st.session_state['customer_phone'] = phone
    if st.button("تسجيل لأول مرة؟"):
        st.session_state['customer_page'] = 'signup'
        st.session_state['customer_signup_step'] = 1

# --- Sign Up Steps ---
def signup_step1():
    st.header("تسجيل عميل جديد - البيانات الأساسية")
    name = st.text_input("الاسم الكامل", key="signup_name")
    phone = st.text_input("رقم الجوال", key="signup_phone")
    password = st.text_input("كلمة المرور", type="password", key="signup_password")
    password2 = st.text_input("تأكيد كلمة المرور", type="password", key="signup_password2")
    if st.button("التالي", key="signup_next1"):
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

# --- Step 2: تحديد الموقع ---
def signup_step2():
    st.header("تحديد الموقع والعنوان")
    geolocator = Nominatim(user_agent="movo_signup")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    # GPS Button
    colgps, colmap = st.columns([1, 8])
    with colgps:
        gps = streamlit_geolocation()
        if gps and gps.get('latitude') and gps.get('longitude'):
            if st.button("استخدم موقعي الحالي (GPS)"):
                st.session_state['customer_location']['lat'] = gps['latitude']
                st.session_state['customer_location']['lon'] = gps['longitude']
                try:
                    location = reverse((gps['latitude'], gps['longitude']), language="ar")
                    if location and location.raw and 'address' in location.raw:
                        addr = location.raw['address']
                        st.session_state['customer_address_fields'] = {
                            'city': addr.get('city', addr.get('town', addr.get('village', ''))),
                            'street': addr.get('road', ''),
                            'district': addr.get('suburb', ''),
                            'neighborhood': addr.get('neighbourhood', ''),
                            'additional_details': ''
                        }
                except Exception:
                    pass
        else:
            st.info("يرجى السماح للمتصفح بالوصول إلى الموقع لاستخدام GPS")

    # الخريطة في الأعلى
    m = folium.Map(location=[st.session_state['customer_location']['lat'], st.session_state['customer_location']['lon']], zoom_start=15)
    marker = folium.Marker(location=[st.session_state['customer_location']['lat'], st.session_state['customer_location']['lon']], draggable=True)
    marker.add_to(m)
    map_data = st_folium(m, width=700, height=400, key="signup_map")

    # عند تحريك Marker أو الضغط على الخريطة: reverse geocode وتعبئة الحقول
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
        st.session_state['customer_location']['lat'] = lat
        st.session_state['customer_location']['lon'] = lon
        try:
            location = reverse((lat, lon), language="ar")
            if location and location.raw and 'address' in location.raw:
                addr = location.raw['address']
                st.session_state['customer_address_fields'] = {
                    'city': addr.get('city', addr.get('town', addr.get('village', ''))),
                    'street': addr.get('road', ''),
                    'district': addr.get('suburb', ''),
                    'neighborhood': addr.get('neighbourhood', ''),
                    'additional_details': ''
                }
        except Exception:
            pass

    # الحقول النصية في الأسفل
    def update_map_from_fields():
        query = f"{st.session_state['customer_address_fields']['street']} {st.session_state['customer_address_fields']['district']} {st.session_state['customer_address_fields']['neighborhood']} {st.session_state['customer_address_fields']['city']} {st.session_state['customer_address_fields']['additional_details']} سوريا".strip()
        if query:
            location = geocode(query)
            if location:
                st.session_state['customer_location']['lat'] = location.latitude
                st.session_state['customer_location']['lon'] = location.longitude

    city = st.text_input("المدينة", value=st.session_state['customer_address_fields']['city'], key="signup_city", on_change=update_map_from_fields)
    street = st.text_input("الشارع", value=st.session_state['customer_address_fields']['street'], key="signup_street", on_change=update_map_from_fields)
    district = st.text_input("الحي/المنطقة", value=st.session_state['customer_address_fields']['district'], key="signup_district", on_change=update_map_from_fields)
    neighborhood = st.text_input("الحي الفرعي", value=st.session_state['customer_address_fields']['neighborhood'], key="signup_neighborhood", on_change=update_map_from_fields)
    additional_details = st.text_input("تفاصيل إضافية", value=st.session_state['customer_address_fields']['additional_details'], key="signup_additional_details", on_change=update_map_from_fields)

    # حفظ البيانات عند الموافقة
    if st.button("حفظ وإنهاء التسجيل", key="signup_finish"):
        st.session_state['customer_signup_data']['address'] = {
            'city': city,
            'street': street,
            'district': district,
            'neighborhood': neighborhood,
            'additional_details': additional_details
        }
        st.session_state['customer_signup_data']['lat'] = st.session_state['customer_location']['lat']
        st.session_state['customer_signup_data']['lon'] = st.session_state['customer_location']['lon']
        st.session_state['customer_signup_step'] = 3

# --- Step 3: Success ---
def signup_step3():
    st.success("تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.")
    st.balloons()
    st.write("بياناتك:")
    st.json(st.session_state['customer_signup_data'])
    if st.button("العودة لتسجيل الدخول", key="signup_back_to_login"):
        st.session_state['customer_page'] = 'login'
        st.session_state['customer_signup_step'] = 1
        st.session_state['customer_signup_data'] = {}
        st.session_state['customer_location'] = {'lat': 33.5138, 'lon': 36.2765}
        st.session_state['customer_address_fields'] = {'city': '', 'street': '', 'district': '', 'neighborhood': '', 'additional_details': ''}

# --- Main Flow ---
if st.session_state['customer_page'] == 'login':
    if st.session_state['customer_login_step'] == 1:
        login_page()
    elif st.session_state['customer_login_step'] == 3:
        st.success("تم تسجيل الدخول بنجاح!")
        st.header("مرحباً بك في لوحة تحكم العميل")
        st.write(f"رقم الجوال: {st.session_state['customer_phone']}")
        st.write("هنا يمكنك استعراض الطلبات، تعديل بياناتك، والمزيد...")
        if st.button("تسجيل خروج", key="logout_btn"):
            st.session_state['customer_login_step'] = 1
            st.session_state['customer_phone'] = ''
else:
    # Sign Up Flow
    if st.session_state['customer_signup_step'] == 1:
        signup_step1()
    elif st.session_state['customer_signup_step'] == 2:
        signup_step2()
    elif st.session_state['customer_signup_step'] == 3:
        signup_step3() 