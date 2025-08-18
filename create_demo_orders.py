#!/usr/bin/env python3
"""
إنشاء طلبات وهمية في قاعدة البيانات
يستخدم نظام الحالات الجديد
"""

import psycopg2
import random
from datetime import datetime, timedelta
import json

# إعدادات الاتصال
DB_CONFIG = {
    "dbname": "movo_system",
    "user": "postgres",
    "password": "movo2025",
    "host": "localhost",
    "port": "5432",
}

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    return psycopg2.connect(**DB_CONFIG)

def create_demo_orders():
    """إنشاء طلبات وهمية"""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # جلب العملاء والمطاعم والكباتن
        cur.execute("SELECT customer_id FROM customers ORDER BY customer_id")
        customer_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id")
        restaurant_ids = [row[0] for row in cur.fetchall()]
        
        cur.execute("SELECT captain_id FROM captains ORDER BY captain_id")
        captain_ids = [row[0] for row in cur.fetchall()]
        
        if not customer_ids or not restaurant_ids:
            print("❌ لا توجد عملاء أو مطاعم في قاعدة البيانات")
            return
        
        print(f"✓ تم العثور على {len(customer_ids)} عميل و {len(restaurant_ids)} مطعم")
        
        # إنشاء طلبات في حالات مختلفة
        orders_to_create = [
            # طلبات في حالة pending
            {"status": "pending", "count": 5},
            # طلبات في حالة choose_captain
            {"status": "choose_captain", "count": 3},
            # طلبات في حالة processing مع substages مختلفة
            {"status": "processing", "current_stage_name": "waiting_approval", "count": 2},
            {"status": "processing", "current_stage_name": "preparing", "count": 2},
            {"status": "processing", "current_stage_name": "captain_received", "count": 2},
            # طلبات في حالة out_for_delivery
            {"status": "out_for_delivery", "count": 2},
            # طلبات منجزة
            {"status": "delivered", "count": 3},
        ]
        
        total_created = 0
        
        for order_config in orders_to_create:
            status = order_config["status"]
            count = order_config["count"]
            current_stage_name = order_config.get("current_stage_name")
            
            print(f"→ إنشاء {count} طلب في حالة '{status}'")
            
            for i in range(count):
                # اختيار عشوائي
                customer_id = random.choice(customer_ids)
                restaurant_id = random.choice(restaurant_ids)
                captain_id = None
                
                # تعيين كابتن للحالات المناسبة
                if status in ["out_for_delivery", "delivered"] and captain_ids:
                    captain_id = random.choice(captain_ids)
                
                # إنشاء الطلب
                order_data = {
                    "customer_id": customer_id,
                    "restaurant_id": restaurant_id,
                    "captain_id": captain_id,
                    "status": status,
                    "current_stage_name": current_stage_name,
                    "payment_method": random.choice(["cash", "card", "mobile_payment"]),
                    "delivery_method": random.choice(["standard", "express"]),
                    "total_price_customer": round(random.uniform(15.0, 45.0), 2),
                    "total_price_restaurant": round(random.uniform(12.0, 35.0), 2),
                    "delivery_fee": round(random.uniform(3.0, 8.0), 2),
                    "distance_meters": random.randint(500, 5000),
                    "created_at": datetime.now() - timedelta(hours=random.randint(1, 24)),
                }
                
                # إدراج الطلب
                cur.execute("""
                    INSERT INTO orders (
                        customer_id, restaurant_id, captain_id, status, current_stage_name,
                        payment_method, delivery_method, total_price_customer, 
                        total_price_restaurant, delivery_fee, distance_meters, created_at
                    ) VALUES (
                        %(customer_id)s, %(restaurant_id)s, %(captain_id)s, %(status)s, %(current_stage_name)s,
                        %(payment_method)s, %(delivery_method)s, %(total_price_customer)s,
                        %(total_price_restaurant)s, %(delivery_fee)s, %(distance_meters)s, %(created_at)s
                    ) RETURNING order_id
                """, order_data)
                
                order_id = cur.fetchone()[0]
                total_created += 1
                
                # إنشاء عناصر الطلب
                items = [
                    {
                        "item": random.choice(["برجر دجاج", "بيتزا مارجريتا", "شاورما لحم", "سلطة سيزر"]),
                        "qty": random.randint(1, 3),
                        "price": round(random.uniform(8.0, 18.0), 2),
                    }
                ]
                
                # إدراج عناصر الطلب
                cur.execute("""
                    UPDATE orders SET items = %s WHERE order_id = %s
                """, (json.dumps(items), order_id))
                
                print(f"  ✓ تم إنشاء الطلب #{order_id}")
        
        conn.commit()
        print(f"✅ تم إنشاء {total_created} طلب بنجاح")
        
        # عرض إحصائيات الحالات
        cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
        status_counts = cur.fetchall()
        
        print("\n📊 إحصائيات الطلبات:")
        for status, count in status_counts:
            print(f"  {status}: {count} طلب")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ خطأ أثناء إنشاء الطلبات: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 بدء إنشاء الطلبات الوهمية...")
    create_demo_orders()
    print("✨ تم الانتهاء من إنشاء الطلبات الوهمية")
