#!/usr/bin/env python3
"""
توليد البيانات الوهمية لنظام Movo
"""

import psycopg2
import os
from datetime import datetime, timedelta

# إعدادات الاتصال - عدّل هذه القيم حسب إعداداتك
DB_CONFIG = {
    'dbname': 'movo_system',
    'user': 'postgres',
    'password': 'movo2025',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    """الحصول على اتصال قاعدة البيانات"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        print("تأكد من:")
        print("1. تشغيل PostgreSQL")
        print("2. إنشاء قاعدة البيانات 'movo_system'")
        print("3. صحة بيانات الاتصال")
        return None

def clear_existing_data(cursor):
    """حذف البيانات الموجودة"""
    print("🗑️  حذف البيانات الموجودة...")
    
    tables = [
        'order_stage_durations', 'order_timings', 'ratings', 'notes',
        'orders', 'menu_item_options', 'menu_items', 'restaurant_phones',
        'customer_addresses', 'customers', 'restaurants', 'captains'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  ✅ تم حذف {table}")
        except Exception as e:
            print(f"  ⚠️  {table}: {e}")

def reset_sequences(cursor):
    """إعادة تعيين التسلسلات"""
    print("🔄 إعادة تعيين التسلسلات...")
    
    sequences = [
        'customers_customer_id_seq',
        'restaurants_restaurant_id_seq', 
        'captains_captain_id_seq',
        'orders_order_id_seq'
    ]
    
    for seq in sequences:
        try:
            cursor.execute(f"ALTER SEQUENCE {seq} RESTART WITH 1")
            print(f"  ✅ تم إعادة تعيين {seq}")
        except Exception as e:
            print(f"  ⚠️  {seq}: {e}")

def insert_customers(cursor):
    """إدراج العملاء"""
    print("👥 إدراج العملاء...")
    
    customers = [
        ('أحمد محمد', '+963991234567'),
        ('فاطمة علي', '+963992345678'),
        ('محمد حسن', '+963993456789'),
        ('سارة أحمد', '+963994567890'),
        ('علي محمود', '+963995678901'),
        ('نور الدين', '+963996789012'),
        ('ليلى كريم', '+963997890123'),
        ('حسن عباس', '+963998901234'),
        ('زينب محمد', '+963999012345'),
        ('محمود أحمد', '+963990123456')
    ]
    
    for name, phone in customers:
        cursor.execute(
            "INSERT INTO customers (name, phone) VALUES (%s, %s)",
            (name, phone)
        )
    
    print(f"  ✅ تم إدراج {len(customers)} عميل")

def insert_restaurants(cursor):
    """إدراج المطاعم"""
    print("🍽️  إدراج المطاعم...")
    
    restaurants = [
        ('مطعم باب الحارة', 33.516, 36.277, 20, 'online', 'available'),
        ('مطعم الشام', 33.514, 36.279, 25, 'online', 'available'),
        ('مطعم دمشق القديمة', 33.518, 36.274, 30, 'online', 'available'),
        ('مطعم الأصالة', 33.512, 36.275, 22, 'online', 'available'),
        ('مطعم النكهة', 33.520, 36.280, 18, 'online', 'available'),
        ('مطعم الطعم الطيب', 33.515, 36.276, 28, 'online', 'available'),
        ('مطعم السعادة', 33.517, 36.278, 24, 'online', 'available'),
        ('مطعم الأمانة', 33.513, 36.273, 26, 'online', 'available')
    ]
    
    for name, lat, lng, prep_time, status, availability in restaurants:
        cursor.execute("""
            INSERT INTO restaurants (name, latitude, longitude, estimated_preparation_time, status, availability) 
            VALUES (%s, %s, %s, %s, %s::restaurant_status_enum, %s::restaurant_availability_enum)
        """, (name, lat, lng, prep_time, status, availability))
    
    print(f"  ✅ تم إدراج {len(restaurants)} مطعم")

def insert_captains(cursor):
    """إدراج الكباتن"""
    print("🚗 إدراج الكباتن...")
    
    captains = [
        ('الكابتن أحمد', '+963991111111', '+963992222222', 'motorcycle', 4.5, True),
        ('الكابتن سامر', '+963993333333', '+963994444444', 'car', 4.8, True),
        ('الكابتن ليلى', '+963995555555', '+963996666666', 'motorcycle', 4.2, True),
        ('الكابتن محمد', '+963997777777', '+963998888888', 'car', 4.6, True),
        ('الكابتن علي', '+963999999999', '+963990000000', 'motorcycle', 4.4, True)
    ]
    
    for name, phone, alt_phone, vehicle, performance, available in captains:
        cursor.execute("""
            INSERT INTO captains (name, phone, alt_phone, vehicle_type, performance, available) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, phone, alt_phone, vehicle, performance, available))
    
    print(f"  ✅ تم إدراج {len(captains)} كابتن")

def insert_customer_addresses(cursor):
    """إدراج عناوين العملاء"""
    print("🏠 إدراج عناوين العملاء...")
    
    addresses = [
        (1, 'home', 'دمشق', 'شارع الثورة', 'وسط المدينة', 'حي الصالحية', 'مبنى رقم 15', 'طابق 3', 33.516, 36.277, True),
        (1, 'work', 'دمشق', 'شارع بغداد', 'وسط المدينة', 'حي القنوات', 'مبنى رقم 8', 'طابق 2', 33.514, 36.279, False),
        (2, 'home', 'دمشق', 'شارع النصر', 'وسط المدينة', 'حي الميدان', 'مبنى رقم 22', 'طابق 1', 33.518, 36.274, True),
        (3, 'home', 'دمشق', 'شارع العابد', 'وسط المدينة', 'حي باب توما', 'مبنى رقم 12', 'طابق 4', 33.512, 36.275, True),
        (4, 'home', 'دمشق', 'شارع الملك فيصل', 'وسط المدينة', 'حي أبو رمانة', 'مبنى رقم 30', 'طابق 2', 33.520, 36.280, True),
        (5, 'home', 'دمشق', 'شارع 29 أيار', 'وسط المدينة', 'حي القصاع', 'مبنى رقم 18', 'طابق 3', 33.515, 36.276, True),
        (6, 'home', 'دمشق', 'شارع جمال عبد الناصر', 'وسط المدينة', 'حي المهاجرين', 'مبنى رقم 25', 'طابق 1', 33.517, 36.278, True),
        (7, 'home', 'دمشق', 'شارع العفيف', 'وسط المدينة', 'حي ركن الدين', 'مبنى رقم 14', 'طابق 5', 33.513, 36.273, True),
        (8, 'home', 'دمشق', 'شارع بغداد', 'وسط المدينة', 'حي القنوات', 'مبنى رقم 9', 'طابق 2', 33.516, 36.277, True),
        (9, 'home', 'دمشق', 'شارع النصر', 'وسط المدينة', 'حي الميدان', 'مبنى رقم 33', 'طابق 3', 33.514, 36.279, True),
        (10, 'home', 'دمشق', 'شارع العابد', 'وسط المدينة', 'حي باب توما', 'مبنى رقم 7', 'طابق 1', 33.518, 36.274, True)
    ]
    
    for addr in addresses:
        cursor.execute("""
            INSERT INTO customer_addresses (customer_id, address_type, city, street, district, neighborhood, additional_details, extra_details, latitude, longitude, is_default) 
            VALUES (%s, %s::address_type_enum, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, addr)
    
    print(f"  ✅ تم إدراج {len(addresses)} عنوان")

def insert_restaurant_phones(cursor):
    """إدراج أرقام هواتف المطاعم"""
    print("📞 إدراج أرقام هواتف المطاعم...")
    
    phones = [
        (1, '+963111111111', 'primary'),
        (1, '+963111111112', 'whatsapp'),
        (2, '+963222222222', 'primary'),
        (2, '+963222222223', 'business'),
        (3, '+963333333333', 'primary'),
        (3, '+963333333334', 'whatsapp'),
        (4, '+963444444444', 'primary'),
        (5, '+963555555555', 'primary'),
        (5, '+963555555556', 'whatsapp'),
        (6, '+963666666666', 'primary'),
        (7, '+963777777777', 'primary'),
        (8, '+963888888888', 'primary')
    ]
    
    for restaurant_id, phone, phone_type in phones:
        cursor.execute("""
            INSERT INTO restaurant_phones (restaurant_id, phone, phone_type) 
            VALUES (%s, %s, %s::phone_type_enum)
        """, (restaurant_id, phone, phone_type))
    
    print(f"  ✅ تم إدراج {len(phones)} رقم هاتف")

def insert_menu_items(cursor):
    """إدراج الأصناف"""
    print("🍕 إدراج الأصناف...")
    
    items = [
        (1, 'برجر دجاج', 12.50, 0, True),
        (1, 'برجر لحم', 15.00, 5, True),
        (1, 'شاورما دجاج', 8.00, 0, True),
        (1, 'شاورما لحم', 10.00, 0, True),
        (1, 'بطاطس مقلية', 4.00, 0, True),
        (2, 'بيتزا مارجريتا', 18.00, 10, True),
        (2, 'بيتزا بيبروني', 22.00, 0, True),
        (2, 'بيتزا دجاج', 20.00, 5, True),
        (2, 'سلطة سيزر', 12.00, 0, True),
        (3, 'كباب لحم', 16.00, 0, True),
        (3, 'كباب دجاج', 14.00, 0, True),
        (3, 'أرز باللحم', 18.00, 0, True),
        (4, 'منسف لحم', 25.00, 0, True),
        (4, 'منسف دجاج', 22.00, 0, True),
        (5, 'فلافل', 6.00, 0, True),
        (5, 'حمص', 5.00, 0, True),
        (6, 'سمك مشوي', 28.00, 15, True),
        (6, 'جمبري مشوي', 32.00, 0, True),
        (7, 'دجاج مشوي', 20.00, 0, True),
        (7, 'لحم مشوي', 24.00, 0, True),
        (8, 'مشاوي متنوعة', 30.00, 0, True)
    ]
    
    for restaurant_id, name, price, discount, visible in items:
        cursor.execute("""
            INSERT INTO menu_items (restaurant_id, name_item, price, discount_percentage, is_visible) 
            VALUES (%s, %s, %s, %s, %s)
        """, (restaurant_id, name, price, discount, visible))
    
    print(f"  ✅ تم إدراج {len(items)} صنف")

def insert_orders(cursor):
    """إدراج الطلبات"""
    print("📦 إدراج الطلبات...")
    
    now = datetime.now()
    orders = [
        (1, 1, None, 'pending', None, 'cash', 'standard', 25.50, 20.00, 5.50, 1500, now - timedelta(hours=2)),
        (2, 2, None, 'pending', None, 'card', 'express', 30.00, 25.00, 5.00, 2000, now - timedelta(hours=1)),
        (3, 3, None, 'choose_captain', None, 'mobile_payment', 'standard', 28.00, 22.00, 6.00, 1800, now - timedelta(minutes=30)),
        (4, 4, 1, 'processing', 'waiting_approval', 'cash', 'standard', 32.00, 26.00, 6.00, 2200, now - timedelta(minutes=45)),
        (5, 5, 2, 'processing', 'preparing', 'card', 'express', 35.00, 28.00, 7.00, 2500, now - timedelta(minutes=20)),
        (6, 6, 3, 'processing', 'captain_received', 'mobile_payment', 'standard', 38.00, 30.00, 8.00, 2800, now - timedelta(minutes=15)),
        (7, 7, 4, 'out_for_delivery', None, 'cash', 'standard', 42.00, 34.00, 8.00, 3000, now - timedelta(minutes=10)),
        (8, 8, 5, 'delivered', None, 'card', 'express', 45.00, 36.00, 9.00, 3200, now - timedelta(minutes=5)),
        (9, 1, None, 'pending', None, 'mobile_payment', 'standard', 27.50, 22.00, 5.50, 1600, now - timedelta(hours=3)),
        (10, 2, None, 'pending', None, 'cash', 'standard', 33.00, 27.00, 6.00, 1900, now - timedelta(hours=4))
    ]
    
    for order_data in orders:
        cursor.execute("""
            INSERT INTO orders (customer_id, restaurant_id, captain_id, status, current_stage_name, payment_method, delivery_method, total_price_customer, total_price_restaurant, delivery_fee, distance_meters, created_at) 
            VALUES (%s, %s, %s, %s::order_status_enum, %s, %s::payment_method_enum, %s::delivery_method_enum, %s, %s, %s, %s, %s)
        """, order_data)
    
    print(f"  ✅ تم إدراج {len(orders)} طلب")

def insert_order_timings(cursor):
    """إدراج أوقات الطلبات"""
    print("⏰ إدراج أوقات الطلبات...")
    
    now = datetime.now()
    timings = [
        (1, '00:20:00', '00:15:00', None, None, now + timedelta(minutes=35)),
        (2, '00:25:00', '00:12:00', None, None, now + timedelta(minutes=37)),
        (3, '00:30:00', '00:18:00', None, None, now + timedelta(minutes=48)),
        (4, '00:22:00', '00:20:00', '00:25:00', None, now + timedelta(minutes=42)),
        (5, '00:18:00', '00:22:00', '00:20:00', None, now + timedelta(minutes=40)),
        (6, '00:28:00', '00:25:00', '00:30:00', None, now + timedelta(minutes=53)),
        (7, '00:24:00', '00:28:00', '00:26:00', '00:30:00', now + timedelta(minutes=54)),
        (8, '00:26:00', '00:30:00', '00:28:00', '00:32:00', now + timedelta(minutes=58)),
        (9, '00:20:00', '00:16:00', None, None, now + timedelta(minutes=36)),
        (10, '00:25:00', '00:19:00', None, None, now + timedelta(minutes=44))
    ]
    
    for timing_data in timings:
        cursor.execute("""
            INSERT INTO order_timings (order_id, expected_preparation_time, expected_delivery_duration, actual_processing_time, actual_delivery_time, estimated_delivery_time) 
            VALUES (%s, %s::interval, %s::interval, %s::interval, %s::interval, %s)
        """, timing_data)
    
    print(f"  ✅ تم إدراج {len(timings)} توقيت")

def insert_stage_durations(cursor):
    """إدراج مدة المراحل"""
    print("📊 إدراج مدة المراحل...")
    
    durations = [
        (1, 'pending', '00:05:00'),
        (2, 'pending', '00:03:00'),
        (3, 'pending', '00:04:00'),
        (3, 'choose_captain', '00:02:00'),
        (4, 'pending', '00:06:00'),
        (4, 'choose_captain', '00:03:00'),
        (4, 'processing', '00:25:00'),
        (5, 'pending', '00:04:00'),
        (5, 'choose_captain', '00:02:00'),
        (5, 'processing', '00:20:00'),
        (6, 'pending', '00:05:00'),
        (6, 'choose_captain', '00:03:00'),
        (6, 'processing', '00:30:00'),
        (7, 'pending', '00:06:00'),
        (7, 'choose_captain', '00:04:00'),
        (7, 'processing', '00:26:00'),
        (7, 'out_for_delivery', '00:30:00'),
        (8, 'pending', '00:05:00'),
        (8, 'choose_captain', '00:03:00'),
        (8, 'processing', '00:28:00'),
        (8, 'out_for_delivery', '00:32:00'),
        (9, 'pending', '00:04:00'),
        (10, 'pending', '00:06:00')
    ]
    
    for order_id, stage_name, duration in durations:
        cursor.execute("""
            INSERT INTO order_stage_durations (order_id, stage_name, duration) 
            VALUES (%s, %s, %s::interval)
        """, (order_id, stage_name, duration))
    
    print(f"  ✅ تم إدراج {len(durations)} مدة مرحلة")

def insert_ratings(cursor):
    """إدراج تقييمات"""
    print("⭐ إدراج تقييمات...")
    
    ratings = [
        (8, None, 5, 5, 'مطعم ممتاز وطعام لذيذ', 'خدمة سريعة وتوصيل ممتاز'),
        (7, None, 4, 4, 'طعام جيد وسعر معقول', 'التوصيل كان في الوقت المحدد')
    ]
    
    for order_id, restaurant_id, rest_score, order_score, rest_comment, order_comment in ratings:
        cursor.execute("""
            INSERT INTO ratings (order_id, restaurant_id, restaurant_emoji_score, order_emoji_score, restaurant_comment, order_comment) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (order_id, restaurant_id, rest_score, order_score, rest_comment, order_comment))
    
    print(f"  ✅ تم إدراج {len(ratings)} تقييم")

def insert_notes(cursor):
    """إدراج ملاحظات"""
    print("📝 إدراج ملاحظات...")
    
    notes = [
        ('order', 'order', 1, None, 'العميل يفضل التوصيل السريع'),
        ('order', 'order', 2, None, 'طلب خاص: إضافة صلصة إضافية'),
        ('restaurant', 'restaurant', 1, None, 'مطعم نشط ومتعاون'),
        ('captain', 'captain', 1, None, 'كابتن محترف وموثوق')
    ]
    
    for note_type, target_type, reference_id, issue_id, note_text in notes:
        cursor.execute("""
            INSERT INTO notes (note_type, target_type, reference_id, issue_id, note_text) 
            VALUES (%s::note_type_enum, %s::note_target_enum, %s, %s, %s)
        """, (note_type, target_type, reference_id, issue_id, note_text))
    
    print(f"  ✅ تم إدراج {len(notes)} ملاحظة")

def insert_discounts(cursor):
    """إدراج حسومات"""
    print("💰 إدراج حسومات...")
    
    now = datetime.now()
    discounts = [
        ('WELCOME10', 'خصم ترحيبي 10%', 'percentage', 10.00, True, now, now + timedelta(days=30)),
        ('NEWUSER15', 'خصم مستخدم جديد 15%', 'percentage', 15.00, True, now, now + timedelta(days=60)),
        ('SPECIAL20', 'عرض خاص 20%', 'percentage', 20.00, True, now, now + timedelta(days=7))
    ]
    
    for name, description, discount_type, value, is_active, start_date, end_date in discounts:
        cursor.execute("""
            INSERT INTO discounts (name, description, discount_type, value, is_active, start_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, description, discount_type, value, is_active, start_date, end_date))
    
    print(f"  ✅ تم إدراج {len(discounts)} حسم")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء توليد البيانات الوهمية لنظام Movo")
    print("=" * 60)
    
    # الحصول على اتصال قاعدة البيانات
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 1. حذف البيانات الموجودة
        clear_existing_data(cursor)
        
        # 2. إعادة تعيين التسلسلات
        reset_sequences(cursor)
        
        # 3. إدراج البيانات الأساسية
        insert_customers(cursor)
        insert_restaurants(cursor)
        insert_captains(cursor)
        insert_customer_addresses(cursor)
        insert_restaurant_phones(cursor)
        insert_menu_items(cursor)
        
        # 4. إدراج الطلبات والبيانات المرتبطة (معلق مؤقتاً)
        # insert_orders(cursor)
        # insert_order_timings(cursor)
        # insert_stage_durations(cursor)
        
        # 5. إدراج البيانات الإضافية (معلق مؤقتاً)
        # insert_ratings(cursor)
        # insert_notes(cursor)
        # insert_discounts(cursor)
        
        # حفظ التغييرات
        conn.commit()
        
        print("\n🎉 تم توليد البيانات الوهمية بنجاح!")
        print("=" * 60)
        print("✅ تم إنشاء:")
        print("  - 10 عملاء")
        print("  - 8 مطاعم")
        print("  - 5 كباتن")
        print("  - 20 صنف طعام")
        print("  - الطلبات والحسومات معلقة لحل المشكلة")
        print("\n⚠️  ملاحظة: تم تعليق إنشاء الطلبات والحسومات لحل مشكلة الـ trigger")
        
    except Exception as e:
        print(f"❌ خطأ أثناء توليد البيانات: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
