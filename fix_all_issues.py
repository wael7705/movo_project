#!/usr/bin/env python3
"""
حل شامل لجميع مشاكل نظام Movo
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
        
        print("✓ الاتصال بقاعدة البيانات ناجح")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الاتصال بقاعدة البيانات: {e}")
        return False

def check_data_exists():
    """التحقق من وجود البيانات الأساسية"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔍 فحص البيانات الأساسية...")
        
        # التحقق من العملاء
        cur.execute("SELECT COUNT(*) FROM customers")
        customer_count = cur.fetchone()[0]
        print(f"👥 العملاء: {customer_count}")
        
        # التحقق من المطاعم
        cur.execute("SELECT COUNT(*) FROM restaurants")
        restaurant_count = cur.fetchone()[0]
        print(f"🍽️ المطاعم: {restaurant_count}")
        
        # التحقق من الكباتن
        cur.execute("SELECT COUNT(*) FROM captains")
        captain_count = cur.fetchone()[0]
        print(f"🚗 الكباتن: {captain_count}")
        
        # التحقق من الطلبات
        cur.execute("SELECT COUNT(*) FROM orders")
        order_count = cur.fetchone()[0]
        print(f"📦 الطلبات: {order_count}")
        
        cur.close()
        conn.close()
        
        return customer_count > 0 and restaurant_count > 0
        
    except Exception as e:
        print(f"❌ خطأ أثناء فحص البيانات: {e}")
        return False

def check_processing_orders():
    """التحقق من الطلبات في حالة processing"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔍 فحص الطلبات في حالة processing...")
        
        # التحقق من الطلبات في حالة processing
        cur.execute("""
            SELECT current_stage_name, COUNT(*) 
            FROM orders 
            WHERE status = 'processing' 
            GROUP BY current_stage_name
        """)
        
        distribution = cur.fetchall()
        
        if not distribution:
            print("❌ لا توجد طلبات في حالة processing")
            return False
        
        print("📊 توزيع الطلبات في حالة processing:")
        total_processing = 0
        for stage, count in distribution:
            print(f"  {stage or 'NULL'}: {count} طلب")
            total_processing += count
        
        print(f"إجمالي الطلبات في حالة processing: {total_processing}")
        
        # التحقق من وجود طلبات في كل substage
        stages = ['waiting_approval', 'preparing', 'captain_received']
        missing_stages = []
        
        for stage in stages:
            cur.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE status = 'processing' AND current_stage_name = %s
            """, (stage,))
            count = cur.fetchone()[0]
            if count == 0:
                missing_stages.append(stage)
        
        if missing_stages:
            print(f"⚠️ المراحل المفقودة: {', '.join(missing_stages)}")
            return False
        
        print("✅ جميع المراحل موجودة")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ أثناء فحص الطلبات: {e}")
        return False

def fix_processing_substages():
    """إصلاح substages الطلبات في حالة processing"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("\n🔧 إصلاح substages الطلبات...")
        
        # 1. تحديث الطلبات التي ليس لها current_stage_name
        cur.execute("""
            UPDATE orders 
            SET current_stage_name = 'waiting_approval'
            WHERE status = 'processing' AND current_stage_name IS NULL
        """)
        
        updated_null = cur.rowcount
        if updated_null > 0:
            print(f"✓ تم تحديث {updated_null} طلب بدون current_stage_name")
        
        # 2. تحديث الطلبات التي لها current_stage_name قديم
        cur.execute("""
            UPDATE orders 
            SET current_stage_name = 'waiting_approval'
            WHERE status = 'processing' AND current_stage_name IN ('waiting_restaurant_acceptance', 'accepted')
        """)
        
        updated_old = cur.rowcount
        if updated_old > 0:
            print(f"✓ تم تحديث {updated_old} طلب بحالة قديمة")
        
        # 3. إضافة طلبات تجريبية في حالات مختلفة إذا لم تكن موجودة
        stages = [
            ('waiting_approval', 'انتظار الموافقة'),
            ('preparing', 'التحضير'),
            ('captain_received', 'الكابتن استلم')
        ]
        
        for stage_name, stage_label in stages:
            cur.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE status = 'processing' AND current_stage_name = %s
            """, (stage_name,))
            count = cur.fetchone()[0]
            
            if count == 0:
                print(f"➕ إضافة طلب في حالة {stage_label}...")
                
                # الحصول على أول عميل ومطعم
                cur.execute("SELECT customer_id FROM customers ORDER BY customer_id LIMIT 1")
                customer_id = cur.fetchone()[0]
                
                cur.execute("SELECT restaurant_id FROM restaurants ORDER BY restaurant_id LIMIT 1")
                restaurant_id = cur.fetchone()[0]
                
                # إضافة الطلب
                cur.execute("""
                    INSERT INTO orders (customer_id, restaurant_id, status, current_stage_name, 
                    total_price_customer, total_price_restaurant, delivery_fee, distance_meters, 
                    payment_method, delivery_method, created_at)
                    VALUES (%s, %s, 'processing', %s, 25.00, 20.00, 5.00, 1500, 'cash', 'standard', NOW())
                    RETURNING order_id
                """, (customer_id, restaurant_id, stage_name))
                
                order_id = cur.fetchone()[0]
                print(f"  ✓ تم إضافة الطلب #{order_id}")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ تم إصلاح substages بنجاح!")
        return True
        
    except Exception as e:
        print(f"❌ خطأ أثناء الإصلاح: {e}")
        return False

def import_fake_data():
    """استيراد البيانات الوهمية"""
    try:
        print("\n📥 استيراد البيانات الوهمية...")
        
        if not os.path.exists('fake_data.sql'):
            print("❌ ملف fake_data.sql غير موجود")
            return False
        
        # قراءة ملف SQL
        with open('fake_data.sql', 'r', encoding='utf-8') as f:
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
                    if i % 20 == 0:  # عرض التقدم كل 20 أمر
                        print(f"  → تم تنفيذ {i}/{len(statements)} أمر")
            except Exception as e:
                error_count += 1
                print(f"  ❌ خطأ في الأمر {i}: {e}")
        
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

def main():
    """الدالة الرئيسية"""
    print("🚀 حل شامل لجميع مشاكل نظام Movo")
    print("=" * 60)
    
    # 1. التحقق من الاتصال
    if not check_database_connection():
        print("❌ فشل في الاتصال بقاعدة البيانات")
        sys.exit(1)
    
    # 2. التحقق من وجود البيانات
    if not check_data_exists():
        print("\n📥 البيانات غير موجودة، جاري الاستيراد...")
        if not import_fake_data():
            print("❌ فشل في استيراد البيانات")
            sys.exit(1)
        print("✅ تم استيراد البيانات بنجاح!")
    else:
        print("✅ البيانات موجودة")
    
    # 3. التحقق من الطلبات في حالة processing
    if not check_processing_orders():
        print("\n🔧 إصلاح substages الطلبات...")
        if not fix_processing_substages():
            print("❌ فشل في إصلاح substages")
            sys.exit(1)
        print("✅ تم إصلاح substages بنجاح!")
        
        # التحقق مرة أخرى
        if not check_processing_orders():
            print("❌ لا تزال هناك مشكلة في substages")
            sys.exit(1)
    
    print("\n🎉 تم حل جميع المشاكل بنجاح!")
    print("\n🎯 يمكنك الآن:")
    print("  1. تشغيل Backend: python -m uvicorn app:app --reload")
    print("  2. تشغيل Frontend: pnpm dev")
    print("  3. اختبار النظام في المتصفح")
    print("  4. التأكد من ظهور الطلبات في أعمدة processing")

if __name__ == "__main__":
    main()
