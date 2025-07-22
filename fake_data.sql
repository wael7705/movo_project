-- 1. إدراج العملاء
INSERT INTO customers (name, phone, latitude, longitude, membership_type) VALUES
('أحمد علي', '0500000001', 24.7136, 46.6753, 'normal'),
('سارة محمد', '0500000002', 24.7743, 46.7386, 'vip'),
('سامي يوسف', '0500000003', 21.3891, 39.8579, 'movo_plus');

-- 2. إدراج المطاعم
INSERT INTO restaurants (name, latitude, longitude, restaurant_location, status, availability, estimated_preparation_time, price_matches) VALUES
('مطعم الشيف', 24.7136, 46.6753, 'الرياض', 'online', 'available', 20, true),
('مطعم البيتزا', 21.3891, 39.8579, 'جدة', 'online', 'busy', 15, false);

-- 3. إدراج الكباتن
INSERT INTO captains (name, phone, alt_phone, vehicle_type, orders_delivered, performance, available) VALUES
('محمد أحمد', '0500000101', '0500000102', 'دراجة نارية', 150, 4.8, true),
('علي حسن', '0500000103', '0500000104', 'سيارة', 200, 4.9, true);

-- 4. (استخرج الـ IDs الفعلية من قاعدة البيانات)
-- SELECT customer_id, name FROM customers;
-- SELECT restaurant_id, name FROM restaurants;
-- SELECT captain_id, name FROM captains;

-- 5. استخدم الـ IDs الفعلية في الطلبات
INSERT INTO orders (
    customer_id, restaurant_id, captain_id, status, payment_method, delivery_method, time_created, estimated_delivery_time, distance_meters, delivery_fee, total_price_customer, total_price_restaurant, cancel_count_per_day, is_scheduled, call_restaurant_time, select_captain_time, expected_delivery_duration
) VALUES
(1, 1, 1, 'pending', 'cash', 'standard', NOW() - INTERVAL '2 hours', INTERVAL '45 minutes', 1500, 15.00, 50.00, 35.00, 0, false, NULL, NULL, NULL),
-- ... باقي الطلبات مع IDs الصحيحة

-- 6. أكمل باقي السكريبت (ملاحظات، حسومات...)