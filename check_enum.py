import psycopg2

try:
    conn = psycopg2.connect('postgresql://postgres:movo2025@localhost:5432/movo_system')
    cur = conn.cursor()
    
    # التحقق من أن "pending" موجود في الـ enum
    cur.execute("SELECT 'pending'::order_status_enum")
    result = cur.fetchone()
    print(f'pending في الـ enum: {result[0]}')
    
    # محاولة إدراج طلب جديد مباشرة في قاعدة البيانات
    print('\nمحاولة إدراج طلب جديد مباشرة...')
    
    # الحصول على أول عميل ومطعم
    cur.execute('SELECT customer_id FROM customers ORDER BY customer_id LIMIT 1')
    customer_id = cur.fetchone()[0]
    
    cur.execute('SELECT restaurant_id FROM restaurants ORDER BY restaurant_id LIMIT 1')
    restaurant_id = cur.fetchone()[0]
    
    print(f'customer_id: {customer_id}, restaurant_id: {restaurant_id}')
    
    # إدراج طلب جديد
    cur.execute("""
        INSERT INTO orders (customer_id, restaurant_id, status, total_price_customer, total_price_restaurant, delivery_fee, distance_meters)
        VALUES (%s, %s, 'pending'::order_status_enum, %s, %s, %s, %s)
        RETURNING order_id
    """, (customer_id, restaurant_id, 25.00, 20.00, 5.00, 1500))
    
    new_order_id = cur.fetchone()[0]
    print(f'تم إنشاء طلب جديد برقم: {new_order_id}')
    
    # التحقق من الطلب الجديد
    cur.execute('SELECT * FROM orders WHERE order_id = %s', (new_order_id,))
    order_data = cur.fetchone()
    print(f'بيانات الطلب الجديد: {order_data}')
    
    conn.commit()
    conn.close()
    print('تم إنشاء الطلب بنجاح!')
    
except Exception as e:
    print(f'خطأ: {e}')
    if 'conn' in locals():
        conn.rollback()
        conn.close()

