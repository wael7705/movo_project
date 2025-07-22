import psycopg2
import os
import logging

DB_CONFIG = {
    'dbname': 'movo_system',  # عدل اسم القاعدة حسب إعدادك
    'user': 'postgres',   # اسم المستخدم
    'password': 'movo2025', # كلمة المرور
    'host': 'localhost',
    'port': 5432
}
SQL_PATH = 'fake_data.sql'
LOG_PATH = 'insert_fake_data_pg.log'

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def run_sql_statements(conn, statements):
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                if stmt.strip():
                    cur.execute(stmt)
        conn.commit()
        logging.info('SQL statements executed successfully.')
        return True, None
    except Exception as e:
        conn.rollback()
        logging.error(f'Error executing SQL statements: {e}')
        return False, str(e)

def main():
    if not os.path.exists(SQL_PATH):
        print(f'❌ ملف البيانات غير موجود: {SQL_PATH}')
        logging.error(f'SQL file not found: {SQL_PATH}')
        return
    try:
        with open(SQL_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
        # تقسيم السكربت إلى مجموعات من التعليمات
        # حذف البيانات القديمة
        delete_stmts = []
        insert_customers = []
        insert_restaurants = []
        insert_captains = []
        insert_orders = []
        insert_notes = []
        insert_discounts = []
        for stmt in sql.split(';'):
            s = stmt.strip()
            if not s:
                continue
            if s.startswith('DELETE'):
                delete_stmts.append(s+';')
            elif s.startswith('INSERT INTO customers'):
                insert_customers.append(s+';')
            elif s.startswith('INSERT INTO restaurants'):
                insert_restaurants.append(s+';')
            elif s.startswith('INSERT INTO captains'):
                insert_captains.append(s+';')
            elif s.startswith('INSERT INTO orders'):
                insert_orders.append(s+';')
            elif s.startswith('INSERT INTO notes'):
                insert_notes.append(s+';')
            elif s.startswith('INSERT INTO discounts'):
                insert_discounts.append(s+';')
        with psycopg2.connect(**DB_CONFIG) as conn:
            # حذف البيانات القديمة
            ok, err = run_sql_statements(conn, delete_stmts)
            if not ok:
                print(f'❌ خطأ أثناء حذف البيانات القديمة: {err}')
                return
            # إدخال العملاء
            ok, err = run_sql_statements(conn, insert_customers)
            if not ok:
                print(f'❌ خطأ أثناء إدخال العملاء: {err}')
                return
            # إدخال المطاعم
            ok, err = run_sql_statements(conn, insert_restaurants)
            if not ok:
                print(f'❌ خطأ أثناء إدخال المطاعم: {err}')
                return
            # إدخال الكباتن
            ok, err = run_sql_statements(conn, insert_captains)
            if not ok:
                print(f'❌ خطأ أثناء إدخال الكباتن: {err}')
                return
            # إدخال الطلبات
            ok, err = run_sql_statements(conn, insert_orders)
            if not ok:
                print(f'❌ خطأ أثناء إدخال الطلبات: {err}')
                return
            # إدخال الملاحظات
            ok, err = run_sql_statements(conn, insert_notes)
            if not ok:
                print(f'❌ خطأ أثناء إدخال الملاحظات: {err}')
                return
            # إدخال الحسومات
            ok, err = run_sql_statements(conn, insert_discounts)
            if not ok:
                print(f'❌ خطأ أثناء إدخال الحسومات: {err}')
                return
            print('✅ تم إدخال جميع البيانات بنجاح!')
    except Exception as e:
        print(f'❌ خطأ غير متوقع: {e}')
        logging.error(f'Unexpected error: {e}')

if __name__ == '__main__':
    main() 