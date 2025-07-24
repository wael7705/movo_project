import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
from datetime import datetime, timedelta

# إعداد الاتصال بقاعدة البيانات
DB_CONFIG = {
    'dbname': 'movo_system',
    'user': 'postgres',
    'password': 'movo2025',
    'host': 'localhost',
    'port': 5432
}

fake = Faker('ar_SA')
Faker.seed(42)

N_CUSTOMERS = 30
N_RESTAURANTS = 10
N_CAPTAINS = 15
N_ORDERS = 60
N_NOTES = 40
N_DISCOUNTS = 8

ORDER_STATUSES = [
    'pending', 'accepted', 'preparing', 'out_for_delivery', 'delivered',
    'cancelled', 'processing', 'waiting_restaurant_acceptance', 'pick_up_ready'
]
PAYMENT_METHODS = ['cash', 'card', 'mobile_payment', 'online']
DELIVERY_METHODS = ['standard', 'express', 'scheduled', 'pick_up']
MEMBERSHIP_TYPES = ['normal', 'vip', 'movo_plus']

# اتصال بقاعدة البيانات
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# ...existing code...

# 0. توليد المستخدمين وربطهم بالعملاء والكباتن والمطاعم
users = []
for i in range(N_CUSTOMERS):
    phone = f"050{1000000 + i}"
    email = f"customer{i}@example.com"
    password = "hashed_password"
    role = 'customer'
    users.append((phone, email, password, role, True))
for i in range(N_CAPTAINS):
    phone = f"050{2000000 + i}"
    email = f"captain{i}@example.com"
    password = "hashed_password"
    role = 'captain'
    users.append((phone, email, password, role, True))
for i in range(N_RESTAURANTS):
    phone = f"050{3000000 + i}"
    email = f"restaurant{i}@example.com"
    password = "hashed_password"
    role = 'restaurant'
    users.append((phone, email, password, role, True))
execute_values(cursor, """
    INSERT INTO users (phone, email, password, role, is_active)
    VALUES %s RETURNING id
""", users)
user_ids = [row[0] for row in cursor.fetchall()]
customer_user_ids = user_ids[:N_CUSTOMERS]
captain_user_ids = user_ids[N_CUSTOMERS:N_CUSTOMERS+N_CAPTAINS]
restaurant_user_ids = user_ids[N_CUSTOMERS+N_CAPTAINS:]

# ...existing code...

# 1. إدراج العملاء بدون user_id
customers = []
for i in range(N_CUSTOMERS):
    name = fake.name()[:100]
    phone = f"050{1000000 + i}"
    lat = round(random.uniform(21.0, 25.0), 6)
    lng = round(random.uniform(39.0, 47.0), 6)
    membership = random.choice(MEMBERSHIP_TYPES)
    customers.append((name, phone, lat, lng, membership))
execute_values(cursor, """
    INSERT INTO customers (name, phone, latitude, longitude, membership_type)
    VALUES %s RETURNING customer_id
""", customers)
customer_ids = [row[0] for row in cursor.fetchall()]

# 2. إدراج المطاعم بدون user_id
restaurants = []
for i in range(N_RESTAURANTS):
    name = fake.company()[:100]
    lat = round(random.uniform(21.0, 25.0), 6)
    lng = round(random.uniform(39.0, 47.0), 6)
    city = fake.city()[:100]
    status = random.choice(['online', 'offline'])
    avail = random.choice(['available', 'busy'])
    prep_time = random.randint(10, 40)
    price_matches = random.choice([True, False])
    restaurants.append((name, lat, lng, city, status, avail, prep_time, price_matches))
execute_values(cursor, """
    INSERT INTO restaurants (name, latitude, longitude, restaurant_location, status, availability, estimated_preparation_time, price_matches)
    VALUES %s RETURNING restaurant_id
""", restaurants)
restaurant_ids = [row[0] for row in cursor.fetchall()]

# 3. إدراج الكباتن بدون user_id
captains = []
for i in range(N_CAPTAINS):
    name = fake.name()[:100]
    phone = f"050{2000000 + i}"
    alt_phone = f"050{2100000 + i}"
    vehicle = random.choice(['دراجة نارية', 'سيارة', 'دراجة هوائية'])
    delivered = random.randint(0, 300)
    perf = round(random.uniform(3.5, 5.0), 2)
    available = random.choice([True, False])
    captains.append((name, phone, alt_phone, vehicle, delivered, perf, available))
execute_values(cursor, """
    INSERT INTO captains (name, phone, alt_phone, vehicle_type, orders_delivered, performance, available)
    VALUES %s RETURNING captain_id
""", captains)
captain_ids = [row[0] for row in cursor.fetchall()]

# ...existing code for orders, notes, discounts...
# 4. إدراج الطلبات
orders = []
now = datetime.now()
for _ in range(N_ORDERS):
    customer_id = random.choice(customer_ids)
    restaurant_id = random.choice(restaurant_ids)
    captain_id = random.choice(captain_ids)
    status = random.choice(ORDER_STATUSES)
    payment = random.choice(PAYMENT_METHODS)
    delivery = random.choice(DELIVERY_METHODS)
    time_created = now - timedelta(minutes=random.randint(10, 180))  # TIMESTAMP
    prep_time = random.randint(10, 40)
    prep_duration = timedelta(minutes=prep_time)
    expected_delivery_duration = timedelta(minutes=120)  # INTERVAL دائمًا 120 دقيقة
    estimated_delivery_time = timedelta(minutes=prep_time + 120)  # INTERVAL دائمًا أكبر من التحضير بكثير
    call_restaurant_time = time_created + estimated_delivery_time - prep_duration  # TIMESTAMP فقط
    select_captain_time = call_restaurant_time - timedelta(minutes=15)  # TIMESTAMP فقط
    distance = random.randint(500, 3000)
    delivery_fee = round(distance * 0.01, 2)
    total_price_customer = round(max(0, random.uniform(20, 100)), 2)
    total_price_restaurant = round(max(0, total_price_customer - delivery_fee), 2)
    cancel_count = random.randint(0, 2)
    is_scheduled = random.choice([True, False])
    # تأكد من الأنواع
    assert isinstance(time_created, datetime)
    assert isinstance(estimated_delivery_time, timedelta)
    assert isinstance(expected_delivery_duration, timedelta)
    assert isinstance(call_restaurant_time, datetime)
    assert isinstance(select_captain_time, datetime)
    orders.append((customer_id, restaurant_id, captain_id, status, payment, delivery, time_created, estimated_delivery_time, distance, delivery_fee, total_price_customer, total_price_restaurant, cancel_count, is_scheduled, call_restaurant_time, select_captain_time, expected_delivery_duration))
execute_values(cursor, """
    INSERT INTO orders (
        customer_id, restaurant_id, captain_id, status, payment_method, delivery_method, time_created, estimated_delivery_time, distance_meters, delivery_fee, total_price_customer, total_price_restaurant, cancel_count_per_day, is_scheduled, call_restaurant_time, select_captain_time, expected_delivery_duration
    ) VALUES %s RETURNING order_id
""", orders)
order_ids = [row[0] for row in cursor.fetchall()]

# 5. إدراج الملاحظات
notes = []
for _ in range(N_NOTES):
    order_id = random.choice(order_ids)
    note_text = fake.sentence(nb_words=8)[:200]
    notes.append(('order', 'order', order_id, note_text))
execute_values(cursor, """
    INSERT INTO notes (note_type, target_type, reference_id, note_text)
    VALUES %s
""", notes)

# 6. إدراج الحسومات
discounts = []
for _ in range(N_DISCOUNTS):
    name = (fake.word() + ' خصم')[:100]
    desc = fake.sentence(nb_words=10)[:200]
    dtype = random.choice(['percentage', 'fixed', 'free_delivery'])
    value = round(random.uniform(5, 50), 2)
    is_active = random.choice([True, False])
    start_date = now - timedelta(days=random.randint(1, 30))
    end_date = now + timedelta(days=random.randint(1, 30))
    code = fake.lexify(text='??????')[:50]
    applies_to_delivery = random.choice([True, False])
    applies_to_menu_items = random.choice([True, False])
    applies_to_entire_menu = random.choice([True, False])
    restaurant_id = random.choice(restaurant_ids)
    created_by_ai = random.choice([True, False])
    ai_score = round(random.uniform(0, 1), 2)
    min_order_value = round(random.uniform(10, 50), 2)
    usage_limit = random.randint(10, 200)
    created_at = now - timedelta(days=random.randint(1, 30))
    discounts.append((name, desc, dtype, value, is_active, start_date, end_date, code, applies_to_delivery, applies_to_menu_items, applies_to_entire_menu, restaurant_id, created_by_ai, ai_score, min_order_value, usage_limit, created_at))
execute_values(cursor, """
    INSERT INTO discounts (name, description, discount_type, value, is_active, start_date, end_date, code, applies_to_delivery, applies_to_menu_items, applies_to_entire_menu, restaurant_id, created_by_ai, ai_recommendation_score, min_order_value, usage_limit, created_at)
    VALUES %s
""", discounts)

conn.commit()
cursor.close()
conn.close()
print(f"✅ تم إدراج بيانات وهمية: {N_CUSTOMERS} عميل، {N_RESTAURANTS} مطعم، {N_CAPTAINS} كابتن، {N_ORDERS} طلب، {N_NOTES} ملاحظة، {N_DISCOUNTS} حسم.") 