import random
from datetime import datetime
from faker import Faker
import psycopg2

# ========= إعدادات الاتصال =========
DB = {
    "dbname": "movo_system",
    "user": "postgres",
    "password": "movo2025",
    "host": "localhost",
    "port": "5432",
}

fake = Faker()

# ========= بارامترات التوليد =========
NUM_CUSTOMERS = 25
ADDRESSES_PER_CUSTOMER = (1, 2)      # من .. إلى
NUM_RESTAURANTS = 10
MENU_ITEMS_PER_RESTAURANT = (5, 10)  # لكل مطعم
GROUPS_PER_ITEM = (0, 2)             # عدد مجموعات الخيارات لكل صنف
CHOICES_PER_GROUP = (2, 4)           # خيارات داخل كل مجموعة
SINGLE_ADDONS_PER_ITEM = (0, 2)      # إضافات منفردة (is_group=false)

# ========= دوال مساعدة =========
def get_conn_cursor():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    return conn, cur

def commit_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

def clamp_phone(p: str) -> str:
    # قص إلى 20 محرف لتفادي أخطاء varchar(20)
    return p.replace(" ", "")[:20]

# ========= توليد العملاء + عناوينهم =========
def seed_customers(cur, conn):
    print("→ إدراج العملاء...")
    for _ in range(NUM_CUSTOMERS):
        name = fake.name()
        phone = clamp_phone(fake.phone_number())
        cur.execute(
            "INSERT INTO customers (name, phone) VALUES (%s, %s)",
            (name, phone),
        )
    conn.commit()

    # جلب الـ IDs للربط
    cur.execute("SELECT customer_id FROM customers ORDER BY customer_id")
    customer_ids = [row[0] for row in cur.fetchall()]

    print("→ إدراج عناوين العملاء...")
    for cid in customer_ids:
        count = random.randint(*ADDRESSES_PER_CUSTOMER)
        used_types = set()
        for i in range(count):
            # حاول ننوّع نوع العنوان (home/work/other)
            possible = ['home', 'work', 'other']
            address_type = random.choice([t for t in possible if t not in used_types] or possible)
            used_types.add(address_type)

            city = fake.city()
            street = fake.street_address()
            district = fake.city_suffix()
            neighborhood = fake.street_name()
            additional_details = fake.secondary_address()
            extra_details = fake.text(max_nb_chars=80)
            latitude = round(random.uniform(33.45, 33.55), 8)
            longitude = round(random.uniform(36.20, 36.35), 8)
            is_default = (i == 0)  # أول عنوان افتراضي

            cur.execute(
                """
                INSERT INTO customer_addresses
                (customer_id, address_type, city, street, district, neighborhood,
                additional_details, extra_details, latitude, longitude, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (cid, address_type, city, street, district, neighborhood,
                additional_details, extra_details, latitude, longitude, is_default)
            )
    conn.commit()

# ========= توليد المطاعم + أرقامها =========
def seed_restaurants(cur, conn):
    print("→ إدراج المطاعم...")
    for _ in range(NUM_RESTAURANTS):
        name = fake.company()
        lat = round(random.uniform(33.40, 33.60), 8)
        lon = round(random.uniform(36.20, 36.40), 8)
        prep_time = random.randint(10, 45)  # دقائق
        cur.execute(
            """
            INSERT INTO restaurants (name, latitude, longitude, estimated_preparation_time, status, availability)
            VALUES (%s, %s, %s, %s, 'online', 'available')
            """,
            (name, lat, lon, prep_time),
        )
    conn.commit()

    print("→ إدراج أرقام هواتف المطاعم...")
def insert_restaurant_phones(cur, conn):
    cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id")
    rest_ids = [r[0] for r in cur.fetchall()]
    for rid in rest_ids:
        phone_count = random.randint(1, 3)


        used_types = set()
        for _ in range(phone_count):
            phone = clamp_phone(fake.phone_number())
            # phone_type_enum: primary, secondary, whatsapp, business, admin
            candidates = ['primary', 'secondary', 'whatsapp', 'business']
            phone_type = random.choice([t for t in candidates if t not in used_types] or candidates)
            used_types.add(phone_type)

            cur.execute(
                "INSERT INTO restaurant_phones (restaurant_id, phone, phone_type) VALUES (%s, %s, %s)",
                (rid, phone, phone_type),
            )
    conn.commit()

# ========= توليد الأصناف + المجموعات + الخيارات =========
def seed_menu(cur, conn):
    print("→ إدراج الأصناف وإضافاتها...")
    cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id")
    rest_ids = [r[0] for r in cur.fetchall()]

    for rid in rest_ids:
        num_items = random.randint(*MENU_ITEMS_PER_RESTAURANT)
        for _ in range(num_items):
            name_item = fake.word().capitalize() + " " + random.choice(["Burger","Wrap","Salad","Pizza","Plate","Box"])
            price = round(random.uniform(2.0, 15.0), 2)
            discount = random.choice([0, 5, 10])  # %
            is_visible = True

            cur.execute(
                """
                INSERT INTO menu_items (restaurant_id, name_item, price, discount_percentage, is_visible)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING item_id
                """,
                (rid, name_item, price, discount, is_visible),
            )
            item_id = cur.fetchone()[0]

            # مجموعات خيارات (is_group = TRUE)
            groups_count = random.randint(*GROUPS_PER_ITEM)
            for _g in range(groups_count):
                group_name = random.choice(["Sauces", "Drinks", "Sides", "Cheese", "Bread"])
                is_group = True
                is_required = random.choice([False, False, True])  # غالباً غير إجباري
                max_selection = random.choice([1, 1, 2])
                price_group = 0  # للمجموعة نفسها صفر

                cur.execute(
                    """
                    INSERT INTO menu_item_options
                    (item_id, group_name, is_group, is_required, max_selection, price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (item_id, group_name, is_group, is_required, max_selection, price_group),
                )
                group_id = cur.fetchone()[0]

                # خيارات داخل المجموعة
                num_choices = random.randint(*CHOICES_PER_GROUP)
                for _c in range(num_choices):
                    choice_name = random.choice([
                        "Ketchup", "Mayo", "Mustard", "BBQ", "Garlic", "Spicy",
                        "Coke", "Sprite", "Water", "Fries", "Wedges", "Onion Rings",
                        "Cheddar", "Mozzarella", "Provolone"
                    ])
                    choice_price = round(random.uniform(0, 3), 2)
                    cur.execute(
                        """
                        INSERT INTO option_choices (group_id, choice_name, price, is_available)
                        VALUES (%s, %s, %s, TRUE)
                        """,
                        (group_id, choice_name, choice_price),
                    )

            # إضافات منفردة مباشرة على الصنف (is_group = FALSE)
            singles = random.randint(*SINGLE_ADDONS_PER_ITEM)
            for _s in range(singles):
                add_name = random.choice(["Extra Sauce", "Extra Cheese", "Double Meat", "Bacon", "Avocado"])
                add_price = round(random.uniform(0.5, 4.0), 2)
                cur.execute(
                    """
                    INSERT INTO menu_item_options
                    (item_id, group_name, is_group, is_required, max_selection, price)
                    VALUES (%s, %s, FALSE, FALSE, 1, %s)
                    """,
                    (item_id, add_name, add_price),
                )
    conn.commit()

def seed_captains(cur, conn, num_captains=10):
    print("→ توليد الكباتن...")
    vehicles = ['motorcycle', 'car', 'bicycle']

    for _ in range(num_captains):
        name = fake.name()
        phone = fake.msisdn()[:12]            # ي fits VARCHAR(20)
        alt_phone = (fake.msisdn()[:12] 
                    if random.random() < 0.5 else None)
        vehicle_type = random.choice(vehicles)
        performance = round(random.uniform(3.5, 5.0), 2)  # 3.5–5.00
        available = random.choice([True, False])

        cur.execute("""
            INSERT INTO captains
                (name, phone, alt_phone, vehicle_type, performance, available)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, phone, alt_phone, vehicle_type, performance, available))

    conn.commit()
    print("✓ تم توليد الكباتن بنجاح")


from datetime import datetime, timedelta

def seed_orders(cur, conn, num_orders=30):
    print("→ توليد الطلبات + الأوقات...")

    # ===== IDs موجودة مسبقاً =====
    cur.execute("SELECT customer_id FROM customers ORDER BY customer_id")
    customer_ids = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT restaurant_id, estimated_preparation_time FROM restaurants ORDER BY restaurant_id")
    rest_rows = cur.fetchall()  # [(id, prep_minutes), ...]
    restaurant_ids = [r[0] for r in rest_rows]
    rest_prep_map = {rid: prep for rid, prep in rest_rows}

    cur.execute("SELECT captain_id FROM captains ORDER BY captain_id")
    captain_ids = [r[0] for r in cur.fetchall()]

    if not customer_ids or not restaurant_ids:
        raise RuntimeError("لازم يكون في عملاء ومطاعم قبل توليد الطلبات.")

    # ===== بعض الثوابت =====
    payment_methods = ['cash', 'card', 'mobile_payment', 'online']
    delivery_methods = ['standard', 'express', 'scheduled', 'pick_up']
    order_statuses   = ['pending','accepted','preparing','out_for_delivery','delivered',
                        'processing','waiting_restaurant_acceptance']  # نتجنب cancelled بالبيانات الوهمية

    now = datetime.now()

    def rand_interval(min_sec, max_sec):
        """يرجع timedelta بالثواني ضمن مجال."""
        sec = random.randint(min_sec, max_sec)
        return timedelta(seconds=sec)

    for _ in range(num_orders):
        customer_id  = random.choice(customer_ids)
        restaurant_id = random.choice(restaurant_ids)

        # طريقة التوصيل
        delivery_method = random.choice(delivery_methods)

        # المسافة (متر) و أجرة التوصيل
        distance_meters = random.randint(400, 7000) if delivery_method != 'pick_up' else 0
        delivery_fee    = round(random.uniform(0.5, 4.5), 2) if delivery_method != 'pick_up' else 0.0

        # أسعار
        subtotal_restaurant = round(random.uniform(5, 30), 2)
        total_price_restaurant = subtotal_restaurant
        total_price_customer   = round(total_price_restaurant + delivery_fee, 2)

        # حالة الطلب
        status = random.choice(order_statuses)

        # جدولة
        is_scheduled = False
        scheduled_time = None
        if delivery_method == 'scheduled':
            is_scheduled = True
            # بين ساعتين و6 ساعات قدّام
            scheduled_time = now + timedelta(minutes=random.randint(120, 360))
            # نضبط حالة معقولة للطلب المجدول
            status = random.choice(['pending','processing','waiting_restaurant_acceptance'])

        # الكابتن (لا نعيّنه بالـ pick_up)
        captain_id = None
        if delivery_method != 'pick_up' and status in ['accepted','preparing','out_for_delivery','delivered']:
            if captain_ids:
                captain_id = random.choice(captain_ids)

        # إدخال الطلب
        cur.execute("""
            INSERT INTO orders
                (customer_id, restaurant_id, captain_id, status, payment_method,
                delivery_method, created_at, is_scheduled, scheduled_time,
                distance_meters, delivery_fee, total_price_customer, total_price_restaurant)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING order_id, created_at
        """, (
            customer_id, restaurant_id, captain_id, status, random.choice(payment_methods),
            delivery_method, now, is_scheduled, scheduled_time,
            distance_meters, delivery_fee, total_price_customer, total_price_restaurant
        ))
        order_id, created_at = cur.fetchone()

        # ===== order_timings =====
        # المتوقع للتحضير من جدول المطاعم
        prep_minutes = rest_prep_map.get(restaurant_id, 15)
        expected_preparation_time = timedelta(minutes=prep_minutes)

        # المتوقع للتوصيل حسب المسافة ونوع التوصيل (تقريبي)

        if delivery_method == 'pick_up':
            expected_delivery_duration = timedelta(seconds=0)
        else:
            base = 6 * 60  # 6 دقائق بالثواني
            per_km = 2 * 60  # دقيقتان لكل كم
            km = distance_meters / 1000.0
            expected_delivery_duration = timedelta(seconds=int(base + per_km * km))
            if delivery_method == 'express':
                # أسرع ~20%
                expected_delivery_duration = expected_delivery_duration * 0.8

        # التوقيت المتوقع للتسليم
        if is_scheduled and scheduled_time:
            estimated_delivery_time = scheduled_time
        else:
            estimated_delivery_time = created_at + expected_preparation_time + expected_delivery_duration + timedelta(minutes=6)

        cur.execute("""
            INSERT INTO order_timings
                (order_id, expected_preparation_time, expected_delivery_duration,
                actual_processing_time, actual_delivery_time, estimated_delivery_time)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            order_id,
            expected_preparation_time,
            expected_delivery_duration,
            None,  # actual_processing_time - ممكن نولّدها إذا بدك
            None,  # actual_delivery_time
            estimated_delivery_time
        ))

        # ===== order_stage_durations =====
        # نبني مدد منطقية حسب الحالة النهائية
        stages = []

        # pending دائماً تقريباً
        stages.append(('pending', rand_interval(20, 180)))

        # إذا النظام مرّ بقبول المطعم
        if status in ['accepted','preparing','out_for_delivery','delivered','processing','waiting_restaurant_acceptance']:
            stages.append(('accepted', rand_interval(15, 120)))

        # اختيار كابتن عندما يلزم
        if delivery_method != 'pick_up' and status in ['preparing','out_for_delivery','delivered']:
            stages.append(('captain_selection', rand_interval(20, 180)))

        # التحضير
        if status in ['preparing','out_for_delivery','delivered']:
            # التحضير عادة قريب من المتوقع ±
            prep_low  = max(30, prep_minutes*60 - 120)
            prep_high = prep_minutes*60 + 180
            stages.append(('preparing', rand_interval(prep_low, prep_high)))

        # الخروج للتوصيل
        if delivery_method != 'pick_up' and status in ['out_for_delivery','delivered']:
            # التوصيل قريب من المتوقع
            deliv_low  = max(60, int(expected_delivery_duration.total_seconds()) - 300)
            deliv_high = int(expected_delivery_duration.total_seconds()) + 420
            stages.append(('out_for_delivery', rand_interval(deliv_low, deliv_high)))

        # إدخال المدد
        for sname, sdur in stages:
            cur.execute("""
                INSERT INTO order_stage_durations (order_id, stage_name, duration)
                VALUES (%s, %s, %s)
            """, (order_id, sname, sdur))

    conn.commit()
    print("✓ تم توليد الطلبات والأوقات بنجاح")


# ========= التشغيل =========
if __name__ == "__main__":
    conn = None
    cur = None
    try:
        conn, cur = get_conn_cursor()

        # استدعاءات التوليد بالترتيب
        seed_customers(cur, conn)
        seed_restaurants(cur, conn)
        insert_restaurant_phones(cur, conn)
        seed_captains(cur, conn)
        seed_menu(cur, conn) 
        seed_orders(cur, conn, num_orders=30)

        print("✅ تم توليد البيانات بنجاح")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ خطأ أثناء التوليد: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
