#!/usr/bin/env python3
"""
استيراد البيانات الوهمية لنظام Movo
"""

import psycopg2
import os
import sys

# إعدادات الاتصال
DB_CONFIG = {
    'dbname': 'movo_system',
    'user': 'postgres',
    'password': 'movo2025',
    'host': 'localhost',
    'port': 5432
}

def check_database_connection():
    """التحقق من الاتصال بقاعدة البيانات"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # التحقق من وجود الجداول
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('customers', 'restaurants', 'captains', 'orders')
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"✓ الجداول الموجودة: {', '.join(tables)}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return False

def import_sql_file():
    """استيراد ملف SQL"""
    sql_file = 'fake_data.sql'
    
    if not os.path.exists(sql_file):
        print(f"❌ ملف {sql_file} غير موجود")
        return False
    
    try:
        # قراءة ملف SQL
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # تقسيم إلى أوامر منفصلة
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"✓ تم العثور على {len(statements)} أمر SQL")
        
        # الاتصال وقبول البيانات
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                if statement.strip():
                    cur.execute(statement)
                    success_count += 1
                    if i % 10 == 0:  # عرض التقدم كل 10 أوامر
                        print(f"  → تم تنفيذ {i}/{len(statements)} أمر")
            except Exception as e:
                error_count += 1
                print(f"  ❌ خطأ في الأمر {i}: {e}")
                print(f"     الأمر: {statement[:100]}...")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n✅ تم تنفيذ {success_count} أمر بنجاح")
        if error_count > 0:
            print(f"❌ فشل في تنفيذ {error_count} أمر")
        
        return error_count == 0
        
    except Exception as e:
        print(f"❌ خطأ أثناء استيراد البيانات: {e}")
        return False

def verify_data():
    """التحقق من البيانات المستوردة"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # التحقق من عدد العملاء
        cur.execute("SELECT COUNT(*) FROM customers")
        customer_count = cur.fetchone()[0]
        print(f"✓ عدد العملاء: {customer_count}")
        
        # التحقق من عدد المطاعم
        cur.execute("SELECT COUNT(*) FROM restaurants")
        restaurant_count = cur.fetchone()[0]
        print(f"✓ عدد المطاعم: {restaurant_count}")
        
        # التحقق من عدد الكباتن
        cur.execute("SELECT COUNT(*) FROM captains")
        captain_count = cur.fetchone()[0]
        print(f"✓ عدد الكباتن: {captain_count}")
        
        # التحقق من عدد الطلبات
        cur.execute("SELECT COUNT(*) FROM orders")
        order_count = cur.fetchone()[0]
        print(f"✓ عدد الطلبات: {order_count}")
        
        # التحقق من توزيع حالات الطلبات
        cur.execute("SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY status")
        status_counts = cur.fetchall()
        print("\n📊 توزيع حالات الطلبات:")
        for status, count in status_counts:
            print(f"  {status}: {count} طلب")
        
        cur.close()
        conn.close()
        
        return customer_count > 0 and restaurant_count > 0
        
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من البيانات: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء استيراد البيانات الوهمية...")
    print("=" * 50)
    
    # التحقق من الاتصال
    if not check_database_connection():
        print("❌ فشل في الاتصال بقاعدة البيانات")
        sys.exit(1)
    
    # استيراد البيانات
    print("\n📥 استيراد البيانات...")
    if not import_sql_file():
        print("❌ فشل في استيراد البيانات")
        sys.exit(1)
    
    # التحقق من البيانات
    print("\n🔍 التحقق من البيانات المستوردة...")
    if not verify_data():
        print("❌ البيانات غير مكتملة")
        sys.exit(1)
    
    print("\n✅ تم استيراد البيانات بنجاح!")
    print("\n🎯 يمكنك الآن:")
    print("  1. تشغيل Backend: python -m uvicorn app:app --reload")
    print("  2. تشغيل Frontend: pnpm dev")
    print("  3. إنشاء طلبات وهمية من الواجهة")

if __name__ == "__main__":
    main()
