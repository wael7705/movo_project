#!/usr/bin/env python3
"""
التحقق من الطلبات في حالة processing وتوزيعها
"""

import psycopg2

# إعدادات الاتصال
DB_CONFIG = {
    'dbname': 'movo_system',
    'user': 'postgres',
    'password': 'movo2025',
    'host': 'localhost',
    'port': 5432
}

def check_processing_orders():
    """التحقق من الطلبات في حالة processing"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🔍 فحص الطلبات في حالة processing...")
        print("=" * 50)
        
        # التحقق من جميع الطلبات
        cur.execute("""
            SELECT 
                order_id, 
                status, 
                current_stage_name,
                customer_id,
                restaurant_id
            FROM orders 
            ORDER BY order_id
        """)
        
        orders = cur.fetchall()
        print(f"📊 إجمالي الطلبات: {len(orders)}")
        
        # تصنيف الطلبات حسب الحالة
        status_counts = {}
        processing_orders = []
        
        for order in orders:
            order_id, status, current_stage_name, customer_id, restaurant_id = order
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status == 'processing':
                processing_orders.append({
                    'order_id': order_id,
                    'current_stage_name': current_stage_name,
                    'customer_id': customer_id,
                    'restaurant_id': restaurant_id
                })
        
        print("\n📈 توزيع الطلبات حسب الحالة:")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count} طلب")
        
        print(f"\n🎯 الطلبات في حالة processing: {len(processing_orders)}")
        
        if processing_orders:
            print("\n📋 تفاصيل الطلبات في حالة processing:")
            for order in processing_orders:
                print(f"  الطلب #{order['order_id']}:")
                print(f"    current_stage_name: {order['current_stage_name']}")
                print(f"    customer_id: {order['customer_id']}")
                print(f"    restaurant_id: {order['restaurant_id']}")
                
                # تحديد substage
                stage_name = (order['current_stage_name'] or '').strip().lower()
                if stage_name in ["waiting_approval", "waiting_restaurant_acceptance"]:
                    substage = "waiting_approval"
                elif stage_name in ["preparing", "preparation"]:
                    substage = "preparing"
                elif stage_name in ["captain_received", "ready_for_pickup"]:
                    substage = "captain_received"
                else:
                    substage = "waiting_approval"
                
                print(f"    substage: {substage}")
                print()
        
        # التحقق من وجود عملاء ومطاعم
        cur.execute("SELECT COUNT(*) FROM customers")
        customer_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM restaurants")
        restaurant_count = cur.fetchone()[0]
        
        print(f"👥 العملاء: {customer_count}")
        print(f"🍽️ المطاعم: {restaurant_count}")
        
        cur.close()
        conn.close()
        
        return processing_orders
        
    except Exception as e:
        print(f"❌ خطأ أثناء فحص الطلبات: {e}")
        return []

def fix_processing_orders():
    """إصلاح الطلبات في حالة processing"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔧 إصلاح الطلبات في حالة processing...")
        
        # تحديث الطلبات التي ليس لها current_stage_name
        cur.execute("""
            UPDATE orders 
            SET current_stage_name = 'waiting_approval'
            WHERE status = 'processing' AND current_stage_name IS NULL
        """)
        
        updated_count = cur.rowcount
        print(f"✓ تم تحديث {updated_count} طلب")
        
        # إضافة طلبات في حالات مختلفة للتجربة
        if updated_count == 0:
            print("➕ إضافة طلبات تجريبية في حالات مختلفة...")
            
            # الحصول على أول عميل ومطعم
            cur.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 1")
            customer_id = cur.fetchone()[0]
            
            cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id LIMIT 1")
            restaurant_id = cur.fetchone()[0]
            
            # إضافة طلب في حالة waiting_approval
            cur.execute("""
                INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                payment_method, delivery_method)
                VALUES (%s, %s, 'processing', 'waiting_approval', 25.00, 20.00, 5.00, 1500, 'cash', 'standard')
                RETURNING order_id
            """, (customer_id, restaurant_id))
            order_id1 = cur.fetchone()[0]
            print(f"  ✓ تم إضافة طلب #{order_id1} في حالة waiting_approval")
            
            # إضافة طلب في حالة preparing
            cur.execute("""
                INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                payment_method, delivery_method)
                VALUES (%s, %s, 'processing', 'preparing', 30.00, 25.00, 5.00, 2000, 'card', 'express')
                RETURNING order_id
            """, (customer_id, restaurant_id))
            order_id2 = cur.fetchone()[0]
            print(f"  ✓ تم إضافة طلب #{order_id2} في حالة preparing")
            
            # إضافة طلب في حالة captain_received
            cur.execute("""
                INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                payment_method, delivery_method)
                VALUES (%s, %s, 'processing', 'captain_received', 35.00, 28.00, 7.00, 2500, 'mobile_payment', 'standard')
                RETURNING order_id
            """, (customer_id, restaurant_id))
            order_id3 = cur.fetchone()[0]
            print(f"  ✓ تم إضافة طلب #{order_id3} في حالة captain_received")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ تم الإصلاح بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ أثناء الإصلاح: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 فحص وإصلاح الطلبات في حالة processing")
    print("=" * 60)
    
    # فحص الطلبات
    processing_orders = check_processing_orders()
    
    # إصلاح الطلبات إذا لزم الأمر
    if len(processing_orders) < 3:
        fix_processing_orders()
        
        print("\n🔍 فحص الطلبات بعد الإصلاح:")
        check_processing_orders()
    
    print("\n🎯 يمكنك الآن اختبار تبويب processing في الواجهة")

if __name__ == "__main__":
    main()
