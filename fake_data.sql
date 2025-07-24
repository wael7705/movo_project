-- 0. إدراج المستخدمين
INSERT INTO users (phone, email, password, role, is_active) VALUES
('0500000001', 'customer1@example.com', 'hashed_password', 'customer', true),
('0500000002', 'customer2@example.com', 'hashed_password', 'customer', true),
('0500000101', 'captain1@example.com', 'hashed_password', 'captain', true),
('0500000103', 'captain2@example.com', 'hashed_password', 'captain', true),
('0500000201', 'restaurant1@example.com', 'hashed_password', 'restaurant', true),
('0500000202', 'restaurant2@example.com', 'hashed_password', 'restaurant', true);

-- 1. إدراج العملاء مع 
INSERT INTO customers (name, phone, latitude, longitude, membership_type) VALUES
('أحمد علي', '0500000001', 24.7136, 46.6753, 'normal'),
('سارة محمد', '0500000002', 24.7743, 46.7386, 'vip');

-- 2.إدراج المطاعم مع
INSERT INTO restaurants (name, latitude, longitude, restaurant_location, status, availability, estimated_preparation_time, price_matches) VALUES
('مطعم الشيف', 24.7136, 46.6753, 'الرياض', 'online', 'available', 20, true),
('مطعم البيتزا', 21.3891, 39.8579, 'جدة', 'online', 'busy', 15, false);

-- 3. إدراج الكباتن مع 
INSERT INTO captains (name, phone, alt_phone, vehicle_type, orders_delivered, performance, available) VALUES
('محمد أحمد', '0500000101', '0500000102', 'دراجة نارية', 150, 4.8, true),
('علي حسن', '0500000103', '0500000104', 'سيارة', 200, 4.9, true);

-- 4. الطلبات (استخدم IDs الفعلية)
INSERT INTO orders (
    customer_id, restaurant_id, captain_id, status, payment_method, delivery_method, time_created, estimated_delivery_time, distance_meters, delivery_fee, total_price_customer, total_price_restaurant, cancel_count_per_day, is_scheduled, call_restaurant_time, select_captain_time, expected_delivery_duration
) VALUES
(1, 5, 3, 'pending', 'cash', 'standard', NOW() - INTERVAL '2 hours', INTERVAL '45 minutes', 1500, 15.00, 50.00, 35.00, 0, false, NULL, NULL, NULL),
(2, 6, 4, 'delivered', 'card', 'express', NOW() - INTERVAL '1 hours', INTERVAL '30 minutes', 800, 10.00, 80.00, 60.00, 0, false, NULL, NULL, NULL);

-- 5. يمكنك إضافة ملاحظات وحسومات بنفس المنهجية وربطها بالـ IDs الصحيحة
-- مثال:
-- INSERT INTO notes (note_type, note_target, target_id, content) VALUES ('order', 'order', 1, 'تم التواصل مع العميل');
-- INSERT INTO discounts (discount_type, value, is_active) VALUES ('percentage', 10, true);

-- ... أكمل باقي السكريبت بنفس المنهجية ...