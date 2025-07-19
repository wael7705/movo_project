    -- بيانات وهمية محدثة

    -- بيانات وهمية محدثة للعملاء
    INSERT INTO customers (name, phone, latitude, longitude, membership_type) VALUES
    ('أحمد علي', '0500000001', 24.7136, 46.6753, 'normal'),
    ('سارة محمد', '0500000002', 24.7743, 46.7386, 'vip'),
    ('خالد يوسف', '0500000003', 21.3891, 39.8579, 'movo_plus'),
    ('منى فهد', '0500000004', 26.4207, 50.0888, 'normal'),
    ('عبدالله صالح', '0500000005', 25.3548, 51.1839, 'vip');

    -- بيانات وهمية للمطاعم مع price_matches
    INSERT INTO restaurants (name, latitude, longitude, restaurant_location, delivery_time, status, availability, estimated_preparation_time, price_matches) VALUES
    ('مطعم الشيف', 24.7136, 46.6753, 'الرياض', 30, 'online', 'available', 20, true),
    ('مطعم البيتزا', 21.3891, 39.8579, 'جدة', 25, 'online', 'busy', 15, false),
    ('مطعم البرجر', 26.4207, 50.0888, 'الدمام', 40, 'offline', 'available', 25, true),
    ('مطعم الفلافل', 25.3548, 51.1839, 'الدوحة', 20, 'online', 'available', 10, true),
    ('مطعم المشويات', 24.7743, 46.7386, 'الرياض', 35, 'offline', 'busy', 30, false);

    -- بيانات وهمية للأصناف مع discount_percentage
    INSERT INTO menu_items (restaurant_id, name_item, price, extras, discount_percentage) VALUES
    (1, 'بيتزا مارجريتا', 35.00, '[{"name": "جبنة إضافية", "price": 5.0}]', 10.00),
    (1, 'بيتزا خضار', 40.00, '[{"name": "زيتون", "price": 3.0}]', 0.00),
    (2, 'برجر دجاج', 25.00, '[{"name": "بطاطس", "price": 7.0}]', 15.00),
    (2, 'برجر لحم', 30.00, '[{"name": "جبنة", "price": 4.0}]', 5.00),
    (3, 'فلافل ساندويتش', 10.00, '[{"name": "طحينة", "price": 2.0}]', 0.00),
    (4, 'مشاوي مشكلة', 50.00, '[{"name": "سلطة", "price": 6.0}]', 20.00),
    (5, 'بيتزا ببروني', 38.00, '[{"name": "فطر", "price": 3.0}]', 0.00);

    -- بيانات وهمية للكباتن
    INSERT INTO captains (name, phone, alt_phone, vehicle_type, orders_delivered, performance, available) VALUES
    ('محمد أحمد', '0500000101', '0500000102', 'دراجة نارية', 150, 4.8, true),
    ('علي حسن', '0500000103', '0500000104', 'سيارة', 200, 4.9, true),
    ('أحمد سعيد', '0500000105', '0500000106', 'دراجة نارية', 120, 4.7, false),
    ('خالد عمر', '0500000107', '0500000108', 'سيارة', 180, 4.6, true),
    ('سعد يوسف', '0500000109', '0500000110', 'دراجة نارية', 90, 4.5, true);

    -- بيانات وهمية للحسومات
    INSERT INTO discounts (name, description, discount_type, value, is_active, start_date, end_date, code, applies_to_delivery, applies_to_menu_items, applies_to_entire_menu, restaurant_id, created_by_ai, ai_recommendation_score, min_order_value, usage_limit, created_at) VALUES
    ('حسم توصيل مجاني', 'توصيل مجاني لجميع الطلبات فوق 30 ريال', 'free_delivery', 100.00, true, NOW() - INTERVAL '10 days', NOW() + INTERVAL '10 days', NULL, true, false, false, NULL, false, NULL, 30.00, 100, NOW() - INTERVAL '10 days'),
    ('خصم 10% على البيتزا', 'خصم 10% على جميع أصناف البيتزا', 'percentage', 10.00, true, NOW() - INTERVAL '5 days', NOW() + INTERVAL '5 days', 'PIZZA10', false, true, false, 1, false, NULL, NULL, 50, NOW() - INTERVAL '5 days'),
    ('خصم 20 ريال على الطلبات الكبيرة', 'خصم ثابت للطلبات فوق 100 ريال', 'fixed', 20.00, true, NOW() - INTERVAL '2 days', NOW() + INTERVAL '8 days', 'BIG20', false, false, true, NULL, false, NULL, 100.00, 20, NOW() - INTERVAL '2 days');

    -- بيانات وهمية للطلبات مع قيم زمنية افتراضية
    INSERT INTO orders (
      customer_id, restaurant_id, captain_id, status, payment_method, delivery_method, delivery_fee, total_price_customer, total_price_restaurant, distance_meters,
      time_created, pending_duration, captain_selection_duration, accept_duration, preparation_duration, delivery_duration, processing_time
    ) VALUES
    (1, 1, 1, 'delivered', 'cash', 'standard', 15.00, 50.00, 35.00, 1500, NOW() - INTERVAL '1 hour', INTERVAL '5 minutes', INTERVAL '2 minutes', INTERVAL '3 minutes', INTERVAL '20 minutes', INTERVAL '10 minutes', INTERVAL '40 minutes'),
    (2, 2, 2, 'out_for_delivery', 'card', 'express', 20.00, 45.00, 25.00, 2000, NOW() - INTERVAL '50 minutes', INTERVAL '4 minutes', INTERVAL '2 minutes', INTERVAL '2 minutes', INTERVAL '15 minutes', INTERVAL '8 minutes', INTERVAL '31 minutes'),
    (3, 3, 3, 'preparing', 'mobile_payment', 'standard', 12.00, 22.00, 10.00, 1200, NOW() - INTERVAL '40 minutes', INTERVAL '3 minutes', INTERVAL '1 minutes', INTERVAL '2 minutes', INTERVAL '10 minutes', INTERVAL '0 minutes', INTERVAL '16 minutes'),
    (4, 4, 4, 'accepted', 'cash', 'standard', 18.00, 68.00, 50.00, 1800, NOW() - INTERVAL '30 minutes', INTERVAL '2 minutes', INTERVAL '1 minutes', INTERVAL '1 minutes', INTERVAL '0 minutes', INTERVAL '0 minutes', INTERVAL '5 minutes'),
    (5, 5, 5, 'pending', 'card', 'express', 25.00, 63.00, 38.00, 2500, NOW() - INTERVAL '20 minutes', INTERVAL '1 minutes', INTERVAL '0 minutes', INTERVAL '0 minutes', INTERVAL '0 minutes', INTERVAL '0 minutes', INTERVAL '0 minutes');

    -- بيانات وهمية لربط الحسومات مع الطلبات
    INSERT INTO order_discounts (order_id, discount_id, applied_value) VALUES
    (1, 1, 15.00),
    (1, 2, 5.00),
    (2, 3, 20.00),
    (3, 1, 8.00),
    (4, 2, 7.00);
