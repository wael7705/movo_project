-- ========================================
-- بيانات وهمية أساسية لنظام Movo
-- ========================================

-- حذف البيانات الموجودة
DELETE FROM order_stage_durations;
DELETE FROM order_timings;
DELETE FROM ratings;
DELETE FROM notes;
DELETE FROM orders;
DELETE FROM menu_item_options;
DELETE FROM menu_items;
DELETE FROM restaurant_phones;
DELETE FROM customer_addresses;
DELETE FROM customers;
DELETE FROM restaurants;
DELETE FROM captains;

-- إعادة تعيين التسلسلات
ALTER SEQUENCE customers_customer_id_seq RESTART WITH 1;
ALTER SEQUENCE restaurants_restaurant_id_seq RESTART WITH 1;
ALTER SEQUENCE captains_captain_id_seq RESTART WITH 1;
ALTER SEQUENCE orders_order_id_seq RESTART WITH 1;

-- ========================================
-- إدراج العملاء
-- ========================================
INSERT INTO customers (name, phone) VALUES
('أحمد محمد', '+963991234567'),
('فاطمة علي', '+963992345678'),
('محمد حسن', '+963993456789'),
('سارة أحمد', '+963994567890'),
('علي محمود', '+963995678901'),
('نور الدين', '+963996789012'),
('ليلى كريم', '+963997890123'),
('حسن عباس', '+963998901234'),
('زينب محمد', '+963999012345'),
('محمود أحمد', '+963990123456');

-- ========================================
-- إدراج المطاعم
-- ========================================
INSERT INTO restaurants (name, latitude, longitude, estimated_preparation_time, status, availability) VALUES
('مطعم باب الحارة', 33.516, 36.277, 20, 'online', 'available'),
('مطعم الشام', 33.514, 36.279, 25, 'online', 'available'),
('مطعم دمشق القديمة', 33.518, 36.274, 30, 'online', 'available'),
('مطعم الأصالة', 33.512, 36.275, 22, 'online', 'available'),
('مطعم النكهة', 33.520, 36.280, 18, 'online', 'available'),
('مطعم الطعم الطيب', 33.515, 36.276, 28, 'online', 'available'),
('مطعم السعادة', 33.517, 36.278, 24, 'online', 'available'),
('مطعم الأمانة', 33.513, 36.273, 26, 'online', 'available');

-- ========================================
-- إدراج الكباتن
-- ========================================
INSERT INTO captains (name, phone, alt_phone, vehicle_type, performance, available) VALUES
('الكابتن أحمد', '+963991111111', '+963992222222', 'motorcycle', 4.5, true),
('الكابتن سامر', '+963993333333', '+963994444444', 'car', 4.8, true),
('الكابتن ليلى', '+963995555555', '+963996666666', 'motorcycle', 4.2, true),
('الكابتن محمد', '+963997777777', '+963998888888', 'car', 4.6, true),
('الكابتن علي', '+963999999999', '+963990000000', 'motorcycle', 4.4, true);

-- ========================================
-- إدراج عناوين العملاء
-- ========================================
INSERT INTO customer_addresses (customer_id, address_type, city, street, district, neighborhood, additional_details, extra_details, latitude, longitude, is_default) VALUES
(1, 'home', 'دمشق', 'شارع الثورة', 'وسط المدينة', 'حي الصالحية', 'مبنى رقم 15', 'طابق 3', 33.516, 36.277, true),
(1, 'work', 'دمشق', 'شارع بغداد', 'وسط المدينة', 'حي القنوات', 'مبنى رقم 8', 'طابق 2', 33.514, 36.279, false),
(2, 'home', 'دمشق', 'شارع النصر', 'وسط المدينة', 'حي الميدان', 'مبنى رقم 22', 'طابق 1', 33.518, 36.274, true),
(3, 'home', 'دمشق', 'شارع العابد', 'وسط المدينة', 'حي باب توما', 'مبنى رقم 12', 'طابق 4', 33.512, 36.275, true),
(4, 'home', 'دمشق', 'شارع الملك فيصل', 'وسط المدينة', 'حي أبو رمانة', 'مبنى رقم 30', 'طابق 2', 33.520, 36.280, true),
(5, 'home', 'دمشق', 'شارع 29 أيار', 'وسط المدينة', 'حي القصاع', 'مبنى رقم 18', 'طابق 3', 33.515, 36.276, true),
(6, 'home', 'دمشق', 'شارع جمال عبد الناصر', 'وسط المدينة', 'حي المهاجرين', 'مبنى رقم 25', 'طابق 1', 33.517, 36.278, true),
(7, 'home', 'دمشق', 'شارع العفيف', 'وسط المدينة', 'حي ركن الدين', 'مبنى رقم 14', 'طابق 5', 33.513, 36.273, true),
(8, 'home', 'دمشق', 'شارع بغداد', 'وسط المدينة', 'حي القنوات', 'مبنى رقم 9', 'طابق 2', 33.516, 36.277, true),
(9, 'home', 'دمشق', 'شارع النصر', 'وسط المدينة', 'حي الميدان', 'مبنى رقم 33', 'طابق 3', 33.514, 36.279, true),
(10, 'home', 'دمشق', 'شارع العابد', 'وسط المدينة', 'حي باب توما', 'مبنى رقم 7', 'طابق 1', 33.518, 36.274, true);

-- ========================================
-- إدراج أرقام هواتف المطاعم
-- ========================================
INSERT INTO restaurant_phones (restaurant_id, phone, phone_type) VALUES
(1, '+963111111111', 'primary'),
(1, '+963111111112', 'whatsapp'),
(2, '+963222222222', 'primary'),
(2, '+963222222223', 'business'),
(3, '+963333333333', 'primary'),
(3, '+963333333334', 'whatsapp'),
(4, '+963444444444', 'primary'),
(5, '+963555555555', 'primary'),
(5, '+963555555556', 'whatsapp'),
(6, '+963666666666', 'primary'),
(7, '+963777777777', 'primary'),
(8, '+963888888888', 'primary');

-- ========================================
-- إدراج الأصناف
-- ========================================
INSERT INTO menu_items (restaurant_id, name_item, price, discount_percentage, is_visible) VALUES
(1, 'برجر دجاج', 12.50, 0, true),
(1, 'برجر لحم', 15.00, 5, true),
(1, 'شاورما دجاج', 8.00, 0, true),
(1, 'شاورما لحم', 10.00, 0, true),
(1, 'بطاطس مقلية', 4.00, 0, true),
(2, 'بيتزا مارجريتا', 18.00, 10, true),
(2, 'بيتزا بيبروني', 22.00, 0, true),
(2, 'بيتزا دجاج', 20.00, 5, true),
(2, 'سلطة سيزر', 12.00, 0, true),
(3, 'كباب لحم', 16.00, 0, true),
(3, 'كباب دجاج', 14.00, 0, true),
(3, 'أرز باللحم', 18.00, 0, true),
(4, 'منسف لحم', 25.00, 0, true),
(4, 'منسف دجاج', 22.00, 0, true),
(5, 'فلافل', 6.00, 0, true),
(5, 'حمص', 5.00, 0, true),
(6, 'سمك مشوي', 28.00, 15, true),
(6, 'جمبري مشوي', 32.00, 0, true),
(7, 'دجاج مشوي', 20.00, 0, true),
(7, 'لحم مشوي', 24.00, 0, true),
(8, 'مشاوي متنوعة', 30.00, 0, true);

-- ========================================
-- إدراج طلبات وهمية
-- ========================================
INSERT INTO orders (customer_id, restaurant_id, captain_id, status, current_stage_name, payment_method, delivery_method, total_price_customer, total_price_restaurant, delivery_fee, distance_meters, created_at) VALUES
(1, 1, NULL, 'pending', NULL, 'cash', 'standard', 25.50, 20.00, 5.50, 1500, NOW() - INTERVAL '2 hours'),
(2, 2, NULL, 'pending', NULL, 'card', 'express', 30.00, 25.00, 5.00, 2000, NOW() - INTERVAL '1 hour'),
(3, 3, NULL, 'choose_captain', NULL, 'mobile_payment', 'standard', 28.00, 22.00, 6.00, 1800, NOW() - INTERVAL '30 minutes'),
(4, 4, 1, 'processing', 'waiting_approval', 'cash', 'standard', 32.00, 26.00, 6.00, 2200, NOW() - INTERVAL '45 minutes'),
(5, 5, 2, 'processing', 'preparing', 'card', 'express', 35.00, 28.00, 7.00, 2500, NOW() - INTERVAL '20 minutes'),
(6, 6, 3, 'processing', 'captain_received', 'mobile_payment', 'standard', 38.00, 30.00, 8.00, 2800, NOW() - INTERVAL '15 minutes'),
(7, 7, 4, 'out_for_delivery', NULL, 'cash', 'standard', 42.00, 34.00, 8.00, 3000, NOW() - INTERVAL '10 minutes'),
(8, 8, 5, 'delivered', NULL, 'card', 'express', 45.00, 36.00, 9.00, 3200, NOW() - INTERVAL '5 minutes'),
(9, 1, NULL, 'pending', NULL, 'mobile_payment', 'standard', 27.50, 22.00, 5.50, 1600, NOW() - INTERVAL '3 hours'),
(10, 2, NULL, 'pending', NULL, 'cash', 'standard', 33.00, 27.00, 6.00, 1900, NOW() - INTERVAL '4 hours');

-- ========================================
-- إدراج عناصر الطلبات
-- ========================================
UPDATE orders SET items = '[{"item": "برجر دجاج", "qty": 2, "price": 12.50}, {"item": "بطاطس مقلية", "qty": 1, "price": 4.00}]' WHERE order_id = 1;
UPDATE orders SET items = '[{"item": "بيتزا مارجريتا", "qty": 1, "price": 18.00}, {"item": "سلطة سيزر", "qty": 1, "price": 12.00}]' WHERE order_id = 2;
UPDATE orders SET items = '[{"item": "كباب لحم", "qty": 1, "price": 16.00}, {"item": "أرز باللحم", "qty": 1, "price": 18.00}]' WHERE order_id = 3;
UPDATE orders SET items = '[{"item": "منسف لحم", "qty": 1, "price": 25.00}]' WHERE order_id = 4;
UPDATE orders SET items = '[{"item": "فلافل", "qty": 2, "price": 6.00}, {"item": "حمص", "qty": 1, "price": 5.00}]' WHERE order_id = 5;
UPDATE orders SET items = '[{"item": "سمك مشوي", "qty": 1, "price": 28.00}]' WHERE order_id = 6;
UPDATE orders SET items = '[{"item": "دجاج مشوي", "qty": 1, "price": 20.00}]' WHERE order_id = 7;
UPDATE orders SET items = '[{"item": "مشاوي متنوعة", "qty": 1, "price": 30.00}]' WHERE order_id = 8;
UPDATE orders SET items = '[{"item": "برجر لحم", "qty": 1, "price": 15.00}, {"item": "شاورما دجاج", "qty": 1, "price": 8.00}]' WHERE order_id = 9;
UPDATE orders SET items = '[{"item": "بيتزا بيبروني", "qty": 1, "price": 22.00}, {"item": "سلطة سيزر", "qty": 1, "price": 12.00}]' WHERE order_id = 10;

-- ========================================
-- إدراج أوقات الطلبات
-- ========================================
INSERT INTO order_timings (order_id, expected_preparation_time, expected_delivery_duration, actual_processing_time, actual_delivery_time, estimated_delivery_time) VALUES
(1, '00:20:00', '00:15:00', NULL, NULL, NOW() + INTERVAL '35 minutes'),
(2, '00:25:00', '00:12:00', NULL, NULL, NOW() + INTERVAL '37 minutes'),
(3, '00:30:00', '00:18:00', NULL, NULL, NOW() + INTERVAL '48 minutes'),
(4, '00:22:00', '00:20:00', '00:25:00', NULL, NOW() + INTERVAL '42 minutes'),
(5, '00:18:00', '00:22:00', '00:20:00', NULL, NOW() + INTERVAL '40 minutes'),
(6, '00:28:00', '00:25:00', '00:30:00', NULL, NOW() + INTERVAL '53 minutes'),
(7, '00:24:00', '00:28:00', '00:26:00', '00:30:00', NOW() + INTERVAL '54 minutes'),
(8, '00:26:00', '00:30:00', '00:28:00', '00:32:00', NOW() + INTERVAL '58 minutes'),
(9, '00:20:00', '00:16:00', NULL, NULL, NOW() + INTERVAL '36 minutes'),
(10, '00:25:00', '00:19:00', NULL, NULL, NOW() + INTERVAL '44 minutes');

-- ========================================
-- إدراج مدة المراحل
-- ========================================
INSERT INTO order_stage_durations (order_id, stage_name, duration) VALUES
(1, 'pending', '00:05:00'),
(2, 'pending', '00:03:00'),
(3, 'pending', '00:04:00'),
(3, 'choose_captain', '00:02:00'),
(4, 'pending', '00:06:00'),
(4, 'choose_captain', '00:03:00'),
(4, 'processing', '00:25:00'),
(5, 'pending', '00:04:00'),
(5, 'choose_captain', '00:02:00'),
(5, 'processing', '00:20:00'),
(6, 'pending', '00:05:00'),
(6, 'choose_captain', '00:03:00'),
(6, 'processing', '00:30:00'),
(7, 'pending', '00:06:00'),
(7, 'choose_captain', '00:04:00'),
(7, 'processing', '00:26:00'),
(7, 'out_for_delivery', '00:30:00'),
(8, 'pending', '00:05:00'),
(8, 'choose_captain', '00:03:00'),
(8, 'processing', '00:28:00'),
(8, 'out_for_delivery', '00:32:00'),
(9, 'pending', '00:04:00'),
(10, 'pending', '00:06:00');

-- ========================================
-- إدراج تقييمات
-- ========================================
INSERT INTO ratings (order_id, restaurant_id, restaurant_emoji_score, order_emoji_score, restaurant_comment, order_comment) VALUES
(8, NULL, 5, 5, 'مطعم ممتاز وطعام لذيذ', 'خدمة سريعة وتوصيل ممتاز'),
(7, NULL, 4, 4, 'طعام جيد وسعر معقول', 'التوصيل كان في الوقت المحدد');

-- ========================================
-- إدراج ملاحظات
-- ========================================
INSERT INTO notes (note_type, target_type, reference_id, issue_id, note_text) VALUES
('order', 'order', 1, NULL, 'العميل يفضل التوصيل السريع'),
('order', 'order', 2, NULL, 'طلب خاص: إضافة صلصة إضافية'),
('restaurant', 'restaurant', 1, NULL, 'مطعم نشط ومتعاون'),
('captain', 'captain', 1, NULL, 'كابتن محترف وموثوق');

-- ========================================
-- إدراج حسومات
-- ========================================
INSERT INTO discounts (discount_code, discount_percentage, valid_from, valid_until, max_uses, current_uses, is_active) VALUES
('WELCOME10', 10, NOW(), NOW() + INTERVAL '30 days', 100, 0, true),
('NEWUSER15', 15, NOW(), NOW() + INTERVAL '60 days', 50, 0, true),
('SPECIAL20', 20, NOW(), NOW() + INTERVAL '7 days', 25, 0, true);

COMMIT;
