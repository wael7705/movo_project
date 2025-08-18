import psycopg2

try:
    conn = psycopg2.connect('postgresql://postgres:movo2025@localhost:5432/movo_system')
    cur = conn.cursor()
    
    # التحقق من آخر طلب تم إنشاؤه
    cur.execute('SELECT * FROM orders ORDER BY order_id DESC LIMIT 1')
    latest_order = cur.fetchone()
    
    if latest_order:
        print('آخر طلب تم إنشاؤه:')
        print(f'  order_id: {latest_order[0]}')
        print(f'  customer_id: {latest_order[1]}')
        print(f'  restaurant_id: {latest_order[2]}')
        print(f'  captain_id: {latest_order[3]}')
        print(f'  status: {latest_order[4]}')
        print(f'  current_stage_name: {latest_order[5]}')
        print(f'  payment_method: {latest_order[6]}')
        print(f'  delivery_method: {latest_order[7]}')
        print(f'  created_at: {latest_order[8]}')
        print(f'  is_scheduled: {latest_order[9]}')
        print(f'  scheduled_time: {latest_order[10]}')
        print(f'  distance_meters: {latest_order[11]}')
        print(f'  delivery_fee: {latest_order[12]}')
        print(f'  total_price_customer: {latest_order[13]}')
        print(f'  total_price_restaurant: {latest_order[14]}')
        print(f'  cancel_count_per_day: {latest_order[15]}')
    
    conn.close()
    
except Exception as e:
    print(f'خطأ: {e}')

