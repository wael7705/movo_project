#!/usr/bin/env python3
"""
إصلاح substages الطلبات في حالة processing
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

def fix_processing_substages():
    """إصلاح substages الطلبات في حالة processing"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🔧 إصلاح substages الطلبات في حالة processing...")
        
        # 1. تحديث الطلبات التي ليس لها current_stage_name
        cur.execute("""
            UPDATE orders 
            SET current_stage_name = 'waiting_approval'
            WHERE status = 'processing' AND current_stage_name IS NULL
        """)
        
        updated_null = cur.rowcount
        print(f"✓ تم تحديث {updated_null} طلب بدون current_stage_name")
        
        # 2. تحديث الطلبات التي لها current_stage_name قديم
        cur.execute("""
            UPDATE orders 
            SET current_stage_name = 'waiting_approval'
            WHERE status = 'processing' AND current_stage_name IN ('waiting_restaurant_acceptance', 'accepted')
        """)
        
        updated_old = cur.rowcount
        print(f"✓ تم تحديث {updated_old} طلب بحالة قديمة")
        
        # 3. إضافة طلبات تجريبية في حالات مختلفة إذا لم تكن موجودة
        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE status = 'processing' AND current_stage_name = 'waiting_approval'
        """)
        waiting_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE status = 'processing' AND current_stage_name = 'preparing'
        """)
        preparing_count = cur.fetchone()[0]
        
        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE status = 'processing' AND current_stage_name = 'captain_received'
        """)
        captain_received_count = cur.fetchone()[0]
        
        print(f"\n📊 توزيع الطلبات في حالة processing:")
        print(f"  waiting_approval: {waiting_count}")
        print(f"  preparing: {preparing_count}")
        print(f"  captain_received: {captain_received_count}")
        
        # إضافة طلبات إذا لم تكن موجودة
        if waiting_count == 0 or preparing_count == 0 or captain_received_count == 0:
            print("\n➕ إضافة طلبات تجريبية...")
            
            # الحصول على أول عميل ومطعم
            cur.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 1")
            customer_id = cur.fetchone()[0]
            
            cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id LIMIT 1")
            restaurant_id = cur.fetchone()[0]
            
            # إضافة طلب في حالة waiting_approval إذا لم يكن موجود
            if waiting_count == 0:
                cur.execute("""
                    INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                    total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                    payment_method, delivery_method, created_at)
                    VALUES (%s, %s, 'processing', 'waiting_approval', 25.00, 20.00, 5.00, 1500, 'cash', 'standard', NOW())
                    RETURNING order_id
                """, (customer_id, restaurant_id))
                order_id = cur.fetchone()[0]
                print(f"  ✓ تم إضافة طلب #{order_id} في حالة waiting_approval")
            
            # إضافة طلب في حالة preparing إذا لم يكن موجود
            if preparing_count == 0:
                cur.execute("""
                    INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                    total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                    payment_method, delivery_method, created_at)
                    VALUES (%s, %s, 'processing', 'preparing', 30.00, 25.00, 5.00, 2000, 'card', 'express', NOW())
                    RETURNING order_id
                """, (customer_id, restaurant_id))
                order_id = cur.fetchone()[0]
                print(f"  ✓ تم إضافة طلب #{order_id} في حالة preparing")
            
            # إضافة طلب في حالة captain_received إذا لم يكن موجود
            if captain_received_count == 0:
                cur.execute("""
                    INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                    total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                    payment_method, delivery_method, created_at)
                    VALUES (%s, %s, 'processing', 'captain_received', 35.00, 28.00, 7.00, 2500, 'mobile_payment', 'standard', NOW())
                    RETURNING order_id
                """, (customer_id, restaurant_id))
                order_id = cur.fetchone()[0]
                print(f"  ✓ تم إضافة طلب #{order_id} في حالة captain_received")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n✅ تم الإصلاح بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ أثناء الإصلاح: {e}")

def verify_fix():
    """التحقق من الإصلاح"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔍 التحقق من الإصلاح...")
        
        # التحقق من الطلبات في حالة processing
        cur.execute("""
            SELECT 
                order_id, 
                current_stage_name,
                total_price_customer,
                created_at
            FROM orders 
            WHERE status = 'processing'
            ORDER BY order_id
        """)
        
        processing_orders = cur.fetchall()
        
        print(f"📊 الطلبات في حالة processing: {len(processing_orders)}")
        
        if processing_orders:
            print("\n📋 تفاصيل الطلبات:")
            for order in processing_orders:
                order_id, current_stage_name, total_price, created_at = order
                print(f"  الطلب #{order_id}:")
                print(f"    current_stage_name: {current_stage_name}")
                print(f"    السعر: {total_price}")
                print(f"    تاريخ الإنشاء: {created_at}")
                
                # تحديد substage
                stage_name = (current_stage_name or '').strip().lower()
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
        
        # التحقق من التوزيع
        cur.execute("""
            SELECT current_stage_name, COUNT(*) 
            FROM orders 
            WHERE status = 'processing' 
            GROUP BY current_stage_name
        """)
        
        distribution = cur.fetchall()
        print("📈 توزيع الطلبات:")
        for stage, count in distribution:
            print(f"  {stage or 'NULL'}: {count} طلب")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 إصلاح substages الطلبات في حالة processing")
    print("=" * 60)
    
    # إصلاح الطلبات
    fix_processing_substages()
    
    # التحقق من الإصلاح
    verify_fix()
    
    print("\n🎯 يمكنك الآن اختبار تبويب processing في الواجهة")
    print("📋 يجب أن ترى الطلبات موزعة في الأعمدة الثلاثة:")

if __name__ == "__main__":
    main()
