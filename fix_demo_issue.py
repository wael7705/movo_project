#!/usr/bin/env python3
"""
حل سريع لمشكلة "No customer/restaurant available"
"""

import psycopg2
import sys

# إعدادات الاتصال
DB_CONFIG = {
    'dbname': 'movo_system',
    'user': 'postgres',
    'password': 'movo2025',
    'host': 'localhost',
    'port': 5432
}

def quick_fix():
    """حل سريع بإضافة عميل ومطعم واحد على الأقل"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🔧 إصلاح سريع لمشكلة البيانات الفارغة...")
        
        # التحقق من وجود عملاء
        cur.execute("SELECT COUNT(*) FROM customers")
        customer_count = cur.fetchone()[0]
        
        # التحقق من وجود مطاعم
        cur.execute("SELECT COUNT(*) FROM restaurants")
        restaurant_count = cur.fetchone()[0]
        
        print(f"📊 الحالة الحالية:")
        print(f"  - العملاء: {customer_count}")
        print(f"  -المطاعم: {restaurant_count}")
        
        # إضافة عميل إذا لم يكن موجود
        if customer_count == 0:
            print("➕ إضافة عميل...")
            cur.execute("""
                INSERT INTO customers (name, phone) 
                VALUES ('عميل تجريبي', '+963991234567')
                RETURNING customer_id
            """)
            customer_id = cur.fetchone()[0]
            print(f"  ✓ تم إضافة العميل #{customer_id}")
        else:
            print("✓ العملاء موجودون")
        
        # إضافة مطعم إذا لم يكن موجود
        if restaurant_count == 0:
            print("➕ إضافة مطعم...")
            cur.execute("""
                INSERT INTO restaurants (name, latitude, longitude, estimated_preparation_time, status, availability) 
                VALUES ('مطعم تجريبي', 33.516, 36.277, 20, 'online', 'available')
                RETURNING restaurant_id
            """)
            restaurant_id = cur.fetchone()[0]
            print(f"  ✓ تم إضافة المطعم #{restaurant_id}")
        else:
            print("✓ المطاعم موجودون")
        
        # إضافة كابتن إذا لم يكن موجود
        cur.execute("SELECT COUNT(*) FROM captains")
        captain_count = cur.fetchone()[0]
        
        if captain_count == 0:
            print("➕ إضافة كابتن...")
            cur.execute("""
                INSERT INTO captains (name, phone, vehicle_type, performance, available) 
                VALUES ('كابتن تجريبي', '+963991111111', 'motorcycle', 4.5, true)
                RETURNING captain_id
            """)
            captain_id = cur.fetchone()[0]
            print(f"  ✓ تم إضافة الكابتن #{captain_id}")
        else:
            print("✓ الكباتن موجودون")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n✅ تم الإصلاح بنجاح!")
        print("🎯 يمكنك الآن إنشاء طلبات وهمية من الواجهة")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ أثناء الإصلاح: {e}")
        return False

def check_status():
    """التحقق من حالة قاعدة البيانات"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("🔍 فحص حالة قاعدة البيانات...")
        
        # التحقق من الجداول
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('customers', 'restaurants', 'captains', 'orders')
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"📋 الجداول الموجودة: {', '.join(tables)}")
        
        # التحقق من البيانات
        for table in ['customers', 'restaurants', 'captains', 'orders']:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"  {table}: {count} صف")
            except:
                print(f"  {table}: خطأ في الوصول")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ في فحص الحالة: {e}")

def main():
    """الدالة الرئيسية"""
    print("🚀 حل سريع لمشكلة البيانات الفارغة")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        check_status()
        return
    
    if quick_fix():
        print("\n🔍 فحص الحالة بعد الإصلاح:")
        check_status()
    else:
        print("\n❌ فشل في الإصلاح")
        sys.exit(1)

if __name__ == "__main__":
    main()
