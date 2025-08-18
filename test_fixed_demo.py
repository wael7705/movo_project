import requests
import json

def test_demo_creation():
    """اختبار إنشاء طلب ديمو - يجب أن يكون pending"""
    base_url = "http://localhost:8000"
    
    print("🧪 اختبار إنشاء طلب ديمو...")
    
    try:
        # إنشاء طلب ديمو جديد
        response = requests.post(f"{base_url}/api/v1/orders/demo")
        print(f"POST /api/v1/orders/demo → {response.status_code}")
        
        if response.status_code == 200:
            order_data = response.json()
            print(f"✅ تم إنشاء الطلب بنجاح!")
            print(f"   order_id: {order_data.get('order_id')}")
            print(f"   status: {order_data.get('status')}")
            print(f"   current_status: {order_data.get('current_status')}")
            
            # التحقق من أن الحالة pending
            if order_data.get('current_status') == 'pending':
                print("✅ الحالة صحيحة: pending")
            else:
                print(f"❌ الحالة خاطئة: {order_data.get('current_status')} (مطلوب: pending)")
                return False
        else:
            print(f"❌ فشل في إنشاء الطلب: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    print("\n📋 اختبار قائمة الطلبات...")
    
    try:
        # الحصول على قائمة الطلبات
        response = requests.get(f"{base_url}/api/v1/orders")
        print(f"GET /api/v1/orders → {response.status_code}")
        
        if response.status_code == 200:
            orders = response.json()
            print(f"   إجمالي الطلبات: {len(orders)}")
            
            # البحث عن الطلب الجديد
            latest_order = None
            for order in orders:
                if order.get('order_id') == order_data.get('order_id'):
                    latest_order = order
                    break
            
            if latest_order:
                print(f"✅ تم العثور على الطلب الجديد في القائمة")
                print(f"   status: {latest_order.get('status')}")
                print(f"   current_status: {latest_order.get('current_status')}")
            else:
                print("❌ لم يتم العثور على الطلب الجديد في القائمة")
                return False
        else:
            print(f"❌ فشل في الحصول على قائمة الطلبات: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    print("\n🔍 اختبار فلترة الطلبات...")
    
    try:
        # اختبار فلترة pending
        response = requests.get(f"{base_url}/api/v1/orders?order_status=pending")
        print(f"GET /api/v1/orders?order_status=pending → {response.status_code}")
        
        if response.status_code == 200:
            pending_orders = response.json()
            print(f"   الطلبات في تبويب pending: {len(pending_orders)}")
            
            # التحقق من وجود الطلب الجديد في pending
            found_in_pending = any(order.get('order_id') == order_data.get('order_id') for order in pending_orders)
            if found_in_pending:
                print("✅ الطلب الجديد موجود في تبويب pending")
            else:
                print("❌ الطلب الجديد غير موجود في تبويب pending")
                return False
        else:
            print(f"❌ فشل في فلترة pending: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    print("\n✅ جميع الاختبارات نجحت!")
    return True

if __name__ == "__main__":
    success = test_demo_creation()
    if success:
        print("\n🎉 الحل يعمل بشكل صحيح!")
    else:
        print("\n💥 هناك مشكلة في الحل!")
