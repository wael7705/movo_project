-- =============================
-- DROP TABLES & TYPES IF EXISTS
-- =============================
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS notes CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS captains CASCADE;
DROP TABLE IF EXISTS menu_items CASCADE;
DROP TABLE IF EXISTS restaurants CASCADE;
DROP TABLE IF EXISTS customer_phones CASCADE;
DROP TABLE IF EXISTS restaurant_phones CASCADE;
DROP TABLE IF EXISTS customer_addresses CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS weather_log CASCADE;
DROP TABLE IF EXISTS issues CASCADE;
DROP TABLE IF EXISTS call_logs CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS discounts CASCADE;
DROP TABLE IF EXISTS order_discounts CASCADE;
DROP TABLE IF EXISTS ai_decisions_log CASCADE;
DROP TABLE IF EXISTS ai_failures CASCADE;
DROP TABLE IF EXISTS alerts_log CASCADE;
DROP TABLE IF EXISTS order_stage_durations CASCADE;
DROP TABLE IF EXISTS menu_item_options CASCADE;

DROP TYPE IF EXISTS membership_type_enum CASCADE;
DROP TYPE IF EXISTS restaurant_status_enum CASCADE;
DROP TYPE IF EXISTS restaurant_availability_enum CASCADE;
DROP TYPE IF EXISTS order_status_enum CASCADE;
DROP TYPE IF EXISTS phone_type_enum CASCADE;
DROP TYPE IF EXISTS address_type_enum CASCADE;
DROP TYPE IF EXISTS note_type_enum CASCADE;
DROP TYPE IF EXISTS note_target_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS delivery_method_enum CASCADE;
DROP TYPE IF EXISTS employee_role_enum CASCADE;

-- =============
-- CREATE TYPES
-- =============
CREATE TYPE membership_type_enum AS ENUM ('normal', 'vip', 'movo_plus');
CREATE TYPE restaurant_status_enum AS ENUM ('online', 'offline');
CREATE TYPE restaurant_availability_enum AS ENUM ('available', 'busy');
CREATE TYPE order_status_enum AS ENUM ('pending', 'accepted', 'preparing', 'out_for_delivery', 'delivered', 'cancelled', 'processing', 'waiting_restaurant_acceptance', 'pick_up_ready');
CREATE TYPE phone_type_enum AS ENUM ('primary', 'secondary', 'whatsapp', 'business', 'admin');
CREATE TYPE address_type_enum AS ENUM ('home', 'work', 'other');
CREATE TYPE note_type_enum AS ENUM ('customer', 'restaurant', 'captain', 'order', 'issue');
CREATE TYPE note_target_enum AS ENUM ('customer', 'restaurant', 'captain', 'order', 'issue');
CREATE TYPE payment_method_enum AS ENUM ('cash', 'card', 'mobile_payment', 'online');
CREATE TYPE delivery_method_enum AS ENUM ('standard', 'express', 'scheduled', 'pick_up');
CREATE TYPE employee_role_enum AS ENUM ('admin', 'supervisor', 'staff');

-- =============
-- USER ROLES ENUM
-- =============
--DO $$ BEGIN
--    CREATE TYPE user_role_enum AS ENUM ('customer', 'captain', 'restaurant', 'data_entry', 'call_center_agent', 'call_center_supervisor', 'admin', 'ai');
--EXCEPTION WHEN duplicate_object THEN null; END $$;

-- ================
-- CREATE TABLES
-- ================

-- USERS TABLE
--CREATE TABLE IF NOT EXISTS users (
    --  id SERIAL PRIMARY KEY,
    --phone VARCHAR(20) UNIQUE NOT NULL,
    --email VARCHAR(100) UNIQUE,
    --password VARCHAR(255) NOT NULL,
    --role user_role_enum NOT NULL,
    --is_active BOOLEAN DEFAULT TRUE,
    --device_id VARCHAR(100),
    --created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
--);

-- Customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    membership_type membership_type_enum DEFAULT 'normal'
);

-- Customer Addresses
CREATE TABLE customer_addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
    address_type address_type_enum DEFAULT 'home',
    city VARCHAR(100) NOT NULL,
    street VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    neighborhood VARCHAR(100),
    additional_details TEXT,
    extra_details TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_default BOOLEAN DEFAULT false
);

-- Restaurants
CREATE TABLE restaurants (
    restaurant_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    restaurant_location VARCHAR(200),
    status restaurant_status_enum DEFAULT 'offline',
    availability restaurant_availability_enum DEFAULT 'available',
    estimated_preparation_time INTEGER NOT NULL, -- in minutes
    price_matches BOOLEAN DEFAULT false -- هل السعر مطابق؟
);

-- Restaurant Phones
CREATE TABLE restaurant_phones (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    phone_type phone_type_enum DEFAULT 'primary'
);

-- Menu Items   
CREATE TABLE menu_items (
    item_id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    name_item VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    extras JSONB, -- Array of objects: [{"name": "Cheese", "price": 2.0}, {"name": "Onion Rings", "price": 1.5}]
    discount_percentage NUMERIC(5,2) DEFAULT 0, -- نسبة الحسم على الصنف (0-100)
    is_visible BOOLEAN DEFAULT true -- Controls whether the menu item is visible in the application interface
);

-- Menu Item Options - إضافات الأصناف
CREATE TABLE menu_item_options (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES menu_items(item_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- اسم الإضافة مثل "زيادة جبنة" أو "صوص حار"
    price DECIMAL(10, 2) NOT NULL, -- سعر الإضافة
    is_available BOOLEAN DEFAULT true, -- هل الإضافة متاحة حالياً؟
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Captains
CREATE TABLE captains (
    captain_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    alt_phone VARCHAR(20),
    vehicle_type VARCHAR(50) NOT NULL,
    orders_delivered INTEGER DEFAULT 0,
    performance DECIMAL(3, 2) DEFAULT 5.00, -- Rating out of 5
    available BOOLEAN DEFAULT true
);

-- Orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id),
    captain_id INTEGER REFERENCES captains(captain_id),
    status order_status_enum DEFAULT 'pending',
    payment_method payment_method_enum DEFAULT 'cash',
    delivery_method delivery_method_enum DEFAULT 'standard',
    time_created TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- وقت إنشاء الطلب
    delivered_at TIMESTAMP, -- وقت التسليم الفعلي
    is_scheduled BOOLEAN DEFAULT FALSE, -- هل الطلب مجدول؟
    call_restaurant_time TIMESTAMP WITHOUT TIME ZONE, -- وقت الاتصال بالمطعم
    select_captain_time TIMESTAMP WITHOUT TIME ZONE, -- وقت اختيار الكابتن
    estimated_delivery_time INTERVAL, -- الوقت المتوقع للتسليم
    expected_delivery_duration INTERVAL, -- مدة التوصيل المتوقعة (للتوافق مع order_timings)
    processing_delay INTERVAL DEFAULT INTERVAL '6 minutes', -- مدة معالجة افتراضية
    distance_meters INTEGER, -- المسافة بين المطعم والعميل
    delivery_fee NUMERIC(10,2), -- رسوم التوصيل
    total_price_customer NUMERIC(10,2), -- السعر النهائي للعميل
    total_price_restaurant NUMERIC(10,2), -- فاتورة المطعم
    cancel_count_per_day INTEGER DEFAULT 0, -- عدد مرات الإلغاء في اليوم
    issue TEXT, -- مشكلة مرتبطة بالطلب
    order_note TEXT, -- ملاحظات الطلب
    ai_estimated_total_time INTERVAL GENERATED ALWAYS AS (
        COALESCE(expected_delivery_duration, INTERVAL '0') + INTERVAL '6 minutes'
    ) STORED, -- الوقت الكلي المتوقع (بدون expected_preparation_time)
    CONSTRAINT check_positive_prices CHECK (total_price_customer >= 0 AND total_price_restaurant >= 0 AND delivery_fee >= 0),
    CONSTRAINT check_cancel_count CHECK (cancel_count_per_day >= 0),
    CONSTRAINT check_distance CHECK (distance_meters >= 0)
);

CREATE TABLE order_timings (
    timing_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    expected_preparation_time INTERVAL NOT NULL,
    expected_delivery_duration INTERVAL NOT NULL,
    total_expected_duration INTERVAL GENERATED ALWAYS AS (
        expected_preparation_time + expected_delivery_duration + INTERVAL '6 minutes'
    ) STORED,
    actual_processing_time INTERVAL,
    actual_delivery_time INTERVAL,
    estimated_delivery_time TIMESTAMP,
    CONSTRAINT fk_order_timings_order FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

CREATE TABLE order_stage_durations (
    stage_duration_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    stage_name TEXT NOT NULL,
    duration INTERVAL,
    stage_start_time TIMESTAMP,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather Log
CREATE TABLE weather_log (
    weather_id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    weather_condition VARCHAR(50) NOT NULL, -- sunny, cloudy, rainy, stormy, etc.
    temperature_celsius DECIMAL(4,1) NOT NULL,
    humidity_percent INTEGER CHECK (humidity_percent BETWEEN 0 AND 100),
    wind_speed_kmh DECIMAL(5,2),
    visibility_km DECIMAL(4,2),
    precipitation_mm DECIMAL(5,2) DEFAULT 0,
    recorded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT check_temperature CHECK (temperature_celsius BETWEEN -50 AND 60),
    CONSTRAINT check_wind_speed CHECK (wind_speed_kmh >= 0),
    CONSTRAINT check_visibility CHECK (visibility_km >= 0),
    CONSTRAINT check_precipitation CHECK (precipitation_mm >= 0)
);

-- Employees
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(50), -- قسم العمل (دعم العملاء، المبيعات، التقنية...)
    position VARCHAR(50), -- المنصب الوظيفي
    role employee_role_enum DEFAULT 'staff', -- دور الموظف في النظام (admin, supervisor, staff)
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    -- حقول تقييم الأداء
    total_calls_handled INTEGER DEFAULT 0, -- إجمالي المكالمات المعالجة
    successful_calls INTEGER DEFAULT 0, -- المكالمات الناجحة
    failed_calls INTEGER DEFAULT 0, -- المكالمات الفاشلة
    avg_call_duration INTERVAL, -- متوسط مدة المكالمة
    total_issues_resolved INTEGER DEFAULT 0, -- إجمالي المشاكل المحلولة
    avg_issue_resolution_time INTERVAL, -- متوسط وقت حل المشكلة
    customer_satisfaction_score DECIMAL(3,2) DEFAULT 0.00, -- درجة رضا العملاء (0-5)
    ai_performance_score DECIMAL(3,2) DEFAULT 0.00, -- تقييم الذكاء الاصطناعي للأداء (0-5)
    efficiency_rating DECIMAL(3,2) DEFAULT 0.00, -- تقييم الكفاءة العامة
    -- حقول إضافية للتحليل
    last_performance_review DATE, -- آخر تقييم أداء
    performance_notes TEXT, -- ملاحظات التقييم
    ai_learning_data JSONB -- بيانات تعلم الذكاء الاصطناعي (أنماط، تحسينات، توصيات...)
);

-- Issues (Tickets)
CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE SET NULL,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    status VARCHAR(30), -- مفتوحة/مغلقة/قيد المعالجة...
    category VARCHAR(100), -- تصنيف المشكلة (توصيل، جودة، دفع...)
    root_cause TEXT, -- السبب الجذري
    resolution TEXT, -- طريقة الحل
    ai_classification TEXT, -- تصنيف الذكاء الاصطناعي
    employee_note TEXT -- ملاحظة الموظف النهائية
);

-- Call Logs
CREATE TABLE call_logs (
    call_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE SET NULL,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE SET NULL,
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE SET NULL,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL,
    call_time TIMESTAMP NOT NULL,
    duration INTERVAL,
    call_recording_url TEXT, -- رابط لتسجيل المكالمة
    call_type VARCHAR(20), -- وارد/صادر/دعم/تسويق...
    notes TEXT
);

-- Notes
CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    note_type note_type_enum NOT NULL,
    target_type note_target_enum NOT NULL,
    reference_id INTEGER NOT NULL, -- Unified reference ID for all entity types
    issue_id INTEGER REFERENCES issues(issue_id) ON DELETE SET NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (note_type = 'customer' AND target_type = 'customer') OR
        (note_type = 'restaurant' AND target_type = 'restaurant') OR
        (note_type = 'captain' AND target_type = 'captain') OR
        (note_type = 'order' AND target_type = 'order') OR
        (note_type = 'issue' AND target_type = 'issue')
    )
);

-- Ratings
CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    restaurant_emoji_score INTEGER CHECK (restaurant_emoji_score BETWEEN 1 AND 5), -- تقييم المطعم (1-5)
    order_emoji_score INTEGER CHECK (order_emoji_score BETWEEN 1 AND 5), -- تقييم الطلب (1-5)
    restaurant_comment TEXT, -- تعليق خاص بتقييم المطعم
    order_comment TEXT, -- تعليق خاص بتقييم الطلب
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (restaurant_id IS NOT NULL AND order_id IS NULL) OR
        (restaurant_id IS NULL AND order_id IS NOT NULL)
    )
);

-- =============================
-- DISCOUNTS & PROMOTIONS SYSTEM
-- =============================

-- جدول الحسومات والعروض
CREATE TABLE discounts (
    discount_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL, -- اسم العرض
    description TEXT, -- وصف نصي للعرض
    discount_type VARCHAR(30) NOT NULL, -- نوع الحسم: percentage, fixed, free_delivery, etc.
    value NUMERIC(10,2) NOT NULL, -- قيمة الحسم (نسبة أو مبلغ)
    is_active BOOLEAN DEFAULT true, -- هل العرض فعال؟
    start_date TIMESTAMP, -- تاريخ بداية العرض
    end_date TIMESTAMP, -- تاريخ نهاية العرض
    code VARCHAR(50), -- كود الخصم (إن وجد)
    applies_to_delivery BOOLEAN DEFAULT false, -- هل ينطبق على التوصيل؟
    applies_to_menu_items BOOLEAN DEFAULT false, -- هل ينطبق على أصناف محددة؟
    applies_to_entire_menu BOOLEAN DEFAULT false, -- هل ينطبق على كل الأصناف؟
    restaurant_id INTEGER REFERENCES restaurants(restaurant_id) ON DELETE CASCADE, -- العرض خاص بمطعم معين (اختياري)
    created_by_ai BOOLEAN DEFAULT false, -- هل تم اقتراح العرض من الذكاء الاصطناعي؟ (مستقبلي)
    ai_recommendation_score DECIMAL(3,2), -- درجة توصية الذكاء الاصطناعي (مستقبلي)
    min_order_value NUMERIC(10,2), -- الحد الأدنى للطلب (اختياري)
    usage_limit INTEGER, -- الحد الأقصى لعدد مرات الاستخدام (اختياري)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول ربط العروض مع الطلبات
CREATE TABLE order_discounts (
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    discount_id INTEGER REFERENCES discounts(discount_id) ON DELETE CASCADE,
    applied_value NUMERIC(10,2), -- قيمة الحسم المطبقة فعلياً
    PRIMARY KEY (order_id, discount_id)
);

-- =============================
-- AI & ANALYTICS TABLES
-- =============================

-- AI Decisions Log - سجل قرارات الذكاء الاصطناعي
CREATE TABLE ai_decisions_log (
    decision_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    decision_type VARCHAR(50) NOT NULL, -- نوع القرار: reassign_captain, cancel_order, delay_order, optimize_route, etc.
    decision_result VARCHAR(30) NOT NULL, -- نتيجة القرار: approved, denied, pending, executed, failed
    decision_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ai_model_version VARCHAR(20), -- إصدار نموذج الذكاء الاصطناعي المستخدم
    confidence_score DECIMAL(3,2), -- درجة الثقة في القرار (0-1)
    reasoning TEXT, -- شرح منطق القرار
    notes TEXT, -- ملاحظات إضافية
    execution_duration INTERVAL, -- مدة تنفيذ القرار
    affected_entities JSONB -- الكيانات المتأثرة بالقرار (captain_id, restaurant_id, etc.)
);

-- AI Failures Log - سجل فشل الذكاء الاصطناعي
CREATE TABLE ai_failures (
    failure_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE SET NULL, -- يمكن أن يكون فشل عام غير مرتبط بطلب معين
    failure_module VARCHAR(50) NOT NULL, -- الوحدة التي حدث فيها الفشل: nlp, call_logic, route_optimization, etc.
    error_code VARCHAR(20), -- كود الخطأ
    error_message TEXT NOT NULL, -- رسالة الخطأ التفصيلية
    failure_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_resolved BOOLEAN DEFAULT false, -- هل تم حل المشكلة؟
    resolution_timestamp TIMESTAMP WITHOUT TIME ZONE, -- وقت حل المشكلة
    resolution_method VARCHAR(100), -- طريقة الحل
    resolution_notes TEXT, -- ملاحظات حول الحل
    ai_model_version VARCHAR(20), -- إصدار النموذج عند حدوث الفشل
    stack_trace TEXT, -- تفاصيل تقنية للفشل (للمطورين)
    severity_level VARCHAR(20) DEFAULT 'medium' -- مستوى خطورة الفشل: low, medium, high, critical
);

-- Alerts Log - سجل التنبيهات
CREATE TABLE alerts_log (
    alert_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL, -- نوع التنبيه: delayed_order, abnormal_behavior, system_issue, etc.
    alert_level VARCHAR(20) NOT NULL DEFAULT 'info', -- مستوى التنبيه: info, warning, error, critical
    alert_message TEXT NOT NULL, -- رسالة التنبيه
    alert_data JSONB, -- بيانات إضافية للتنبيه
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITHOUT TIME ZONE, -- وقت حل التنبيه
    is_resolved BOOLEAN DEFAULT false, -- هل تم حل التنبيه؟
    resolved_by INTEGER REFERENCES employees(employee_id) ON DELETE SET NULL, -- الموظف الذي حل التنبيه
    resolution_notes TEXT, -- ملاحظات الحل
    auto_resolved BOOLEAN DEFAULT false, -- هل تم الحل تلقائياً؟
    escalation_level INTEGER DEFAULT 0 -- مستوى التصعيد (0 = لا تصعيد، 1+ = مستويات التصعيد المتتالية)
);

-- =============================
-- VIEWS
-- =============================

CREATE VIEW order_processing_time_view AS
SELECT
    order_id,
    SUM(duration) AS total_processing_time
FROM order_stage_durations
WHERE stage_name IN ('pending', 'assigning_captain', 'restaurant_acceptance', 'preparing')
GROUP BY order_id;

CREATE VIEW order_summary AS
SELECT 
    o.order_id,
    o.status,
    TO_CHAR(COALESCE(pending.duration, INTERVAL '0'), 'MI:SS') as pending_duration_mmss,
    TO_CHAR(COALESCE(accept.duration, INTERVAL '0'), 'MI:SS') as accept_duration_mmss,
    TO_CHAR(COALESCE(captain_selection.duration, INTERVAL '0'), 'MI:SS') as captain_selection_duration_mmss,
    TO_CHAR(COALESCE(preparing.duration, INTERVAL '0'), 'MI:SS') as preparation_duration_mmss,
    TO_CHAR(COALESCE(delivery.duration, INTERVAL '0'), 'MI:SS') as delivery_duration_mmss,
    o.time_created,
    TO_CHAR(o.estimated_delivery_time, 'MI:SS') as estimated_delivery_duration_mmss,
    o.distance_meters,
    o.delivery_fee,
    o.total_price_customer,
    o.total_price_restaurant,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_processing_duration_mmss,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as processing_time_mmss,
    c.name as customer_name,
    r.name as restaurant_name,
    cap.name as captain_name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN captains cap ON o.captain_id = cap.captain_id
LEFT JOIN order_stage_durations pending ON o.order_id = pending.order_id AND pending.stage_name = 'pending'
LEFT JOIN order_stage_durations accept ON o.order_id = accept.order_id AND accept.stage_name = 'accepted'
LEFT JOIN order_stage_durations captain_selection ON o.order_id = captain_selection.order_id AND captain_selection.stage_name = 'captain_selection'
LEFT JOIN order_stage_durations preparing ON o.order_id = preparing.order_id AND preparing.stage_name = 'preparing'
LEFT JOIN order_stage_durations delivery ON o.order_id = delivery.order_id AND delivery.stage_name = 'out_for_delivery';

CREATE OR REPLACE VIEW order_stage_summary AS
SELECT
  order_id,
  stage_name,
  duration,
  recorded_at
FROM order_stage_durations
ORDER BY order_id, recorded_at;

CREATE VIEW restaurant_performance AS
SELECT 
    r.restaurant_id,
    r.name,
    r.restaurant_location,
    COUNT(o.order_id) as total_orders,
    AVG(o.total_price_restaurant) as avg_restaurant_invoice,
    AVG(o.delivery_fee) as avg_delivery_fee,
    AVG(o.total_price_customer) as avg_total_customer_price,
    AVG(o.distance_meters) as avg_delivery_distance_meters,
    AVG(rt.restaurant_emoji_score) as avg_rating,
    COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) as delivered_orders,
    SUM(o.delivery_fee) as total_delivery_fees_generated
FROM restaurants r
LEFT JOIN orders o ON r.restaurant_id = o.restaurant_id
LEFT JOIN ratings rt ON r.restaurant_id = rt.restaurant_id
GROUP BY r.restaurant_id, r.name, r.restaurant_location;

CREATE VIEW order_duration_analytics AS
SELECT 
    o.order_id,
    o.status,
    TO_CHAR(COALESCE(pending.duration, INTERVAL '0'), 'MI:SS') as pending_duration_mmss,
    TO_CHAR(COALESCE(accept.duration, INTERVAL '0'), 'MI:SS') as accept_duration_mmss,
    TO_CHAR(COALESCE(captain_selection.duration, INTERVAL '0'), 'MI:SS') as captain_selection_duration_mmss,
    TO_CHAR(COALESCE(preparing.duration, INTERVAL '0'), 'MI:SS') as preparation_duration_mmss,
    TO_CHAR(COALESCE(delivery.duration, INTERVAL '0'), 'MI:SS') as delivery_duration_mmss,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_duration_mmss,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_processing_duration_mmss,
    CASE 
        WHEN COALESCE(pending.duration, INTERVAL '0') <= INTERVAL '2 minutes' THEN 'Excellent'
        WHEN COALESCE(pending.duration, INTERVAL '0') <= INTERVAL '5 minutes' THEN 'Good'
        WHEN COALESCE(pending.duration, INTERVAL '0') <= INTERVAL '10 minutes' THEN 'Fair'
        ELSE 'Poor'
    END as pending_performance,
    CASE 
        WHEN COALESCE(preparing.duration, INTERVAL '0') <= INTERVAL '10 minutes' THEN 'Excellent'
        WHEN COALESCE(preparing.duration, INTERVAL '0') <= INTERVAL '15 minutes' THEN 'Good'
        WHEN COALESCE(preparing.duration, INTERVAL '0') <= INTERVAL '20 minutes' THEN 'Fair'
        ELSE 'Poor'
    END as preparation_performance,
    CASE 
        WHEN COALESCE(delivery.duration, INTERVAL '0') <= INTERVAL '10 minutes' THEN 'Excellent'
        WHEN COALESCE(delivery.duration, INTERVAL '0') <= INTERVAL '15 minutes' THEN 'Good'
        WHEN COALESCE(delivery.duration, INTERVAL '0') <= INTERVAL '20 minutes' THEN 'Fair'
        ELSE 'Poor'
    END as delivery_performance,
    c.name as customer_name,
    r.name as restaurant_name,
    cap.name as captain_name,
    o.total_price_customer,
    o.delivery_fee,
    o.distance_meters
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN captains cap ON o.captain_id = cap.captain_id
LEFT JOIN order_stage_durations pending ON o.order_id = pending.order_id AND pending.stage_name = 'pending'
LEFT JOIN order_stage_durations accept ON o.order_id = accept.order_id AND accept.stage_name = 'accepted'
LEFT JOIN order_stage_durations captain_selection ON o.order_id = captain_selection.order_id AND captain_selection.stage_name = 'captain_selection'
LEFT JOIN order_stage_durations preparing ON o.order_id = preparing.order_id AND preparing.stage_name = 'preparing'
LEFT JOIN order_stage_durations delivery ON o.order_id = delivery.order_id AND delivery.stage_name = 'out_for_delivery'
WHERE o.status IN ('delivered', 'out_for_delivery', 'preparing', 'accepted');

CREATE VIEW order_duration_flags AS
SELECT 
    o.order_id,
    CASE 
        WHEN COALESCE(pending.duration, INTERVAL '0') > INTERVAL '1 minute 30 seconds' THEN true
        ELSE false
    END as flag_pending,
    CASE 
        WHEN COALESCE(accept.duration, INTERVAL '0') > INTERVAL '1 minute 30 seconds' THEN true
        ELSE false
    END as flag_accept,
    CASE 
        WHEN COALESCE(captain_selection.duration, INTERVAL '0') > INTERVAL '2 minutes' THEN true
        ELSE false
    END as flag_waiting_approval,
    CASE 
        WHEN COALESCE(preparing.duration, INTERVAL '0') > INTERVAL '40 minutes' THEN true
        ELSE false
    END as flag_preparing,
    CASE 
        WHEN COALESCE(delivery.duration, INTERVAL '0') > INTERVAL '30 minutes' THEN true
        ELSE false
    END as flag_delivery,
    CASE 
        WHEN COALESCE(pending.duration, INTERVAL '0') > INTERVAL '1 minute 30 seconds' OR
             COALESCE(accept.duration, INTERVAL '0') > INTERVAL '1 minute 30 seconds' OR
             COALESCE(captain_selection.duration, INTERVAL '0') > INTERVAL '2 minutes' OR
             COALESCE(preparing.duration, INTERVAL '0') > INTERVAL '40 minutes' OR
             COALESCE(delivery.duration, INTERVAL '0') > INTERVAL '30 minutes'
        THEN true
        ELSE false
    END as any_alert,
    TO_CHAR(COALESCE(pending.duration, INTERVAL '0'), 'MI:SS') as pending_duration_mmss,
    TO_CHAR(COALESCE(accept.duration, INTERVAL '0'), 'MI:SS') as accept_duration_mmss,
    TO_CHAR(COALESCE(captain_selection.duration, INTERVAL '0'), 'MI:SS') as captain_selection_duration_mmss,
    TO_CHAR(COALESCE(preparing.duration, INTERVAL '0'), 'MI:SS') as preparation_duration_mmss,
    TO_CHAR(COALESCE(delivery.duration, INTERVAL '0'), 'MI:SS') as delivery_duration_mmss,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_duration_mmss,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_processing_duration_mmss,
    COALESCE(pending.duration, INTERVAL '0') as pending_duration,
    COALESCE(accept.duration, INTERVAL '0') as accept_duration,
    COALESCE(captain_selection.duration, INTERVAL '0') as captain_selection_duration,
    COALESCE(preparing.duration, INTERVAL '0') as preparation_duration,
    COALESCE(delivery.duration, INTERVAL '0') as delivery_duration,
    (COALESCE(pending.duration, INTERVAL '0') + 
     COALESCE(accept.duration, INTERVAL '0') + 
     COALESCE(captain_selection.duration, INTERVAL '0') + 
     COALESCE(preparing.duration, INTERVAL '0') + 
     COALESCE(delivery.duration, INTERVAL '0')) as total_processing_duration,
    o.status,
    c.name as customer_name,
    r.name as restaurant_name,
    cap.name as captain_name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN captains cap ON o.captain_id = cap.captain_id
LEFT JOIN order_stage_durations pending ON o.order_id = pending.order_id AND pending.stage_name = 'pending'
LEFT JOIN order_stage_durations accept ON o.order_id = accept.order_id AND accept.stage_name = 'accepted'
LEFT JOIN order_stage_durations captain_selection ON o.order_id = captain_selection.order_id AND captain_selection.stage_name = 'captain_selection'
LEFT JOIN order_stage_durations preparing ON o.order_id = preparing.order_id AND preparing.stage_name = 'preparing'
LEFT JOIN order_stage_durations delivery ON o.order_id = delivery.order_id AND delivery.stage_name = 'out_for_delivery'
WHERE o.status IN ('delivered', 'out_for_delivery', 'preparing', 'accepted');

CREATE VIEW order_timing_validation AS
SELECT 
    o.order_id,
    o.status,
    CASE 
        WHEN o.time_created IS NOT NULL AND o.estimated_delivery_time IS NOT NULL
        THEN o.estimated_delivery_time > INTERVAL '0'
        ELSE true
    END as estimated_delivery_valid,
    CASE 
        WHEN pending.duration IS NOT NULL
        THEN pending.duration >= INTERVAL '0 seconds' AND pending.duration <= INTERVAL '30 minutes'
        ELSE true
    END as pending_duration_valid,
    CASE 
        WHEN accept.duration IS NOT NULL
        THEN accept.duration >= INTERVAL '0 seconds' AND accept.duration <= INTERVAL '30 minutes'
        ELSE true
    END as accept_duration_valid,
    CASE 
        WHEN captain_selection.duration IS NOT NULL
        THEN captain_selection.duration >= INTERVAL '0 seconds' AND captain_selection.duration <= INTERVAL '30 minutes'
        ELSE true
    END as captain_selection_duration_valid,
    CASE 
        WHEN preparing.duration IS NOT NULL
        THEN preparing.duration >= INTERVAL '0 seconds' AND preparing.duration <= INTERVAL '30 minutes'
        ELSE true
    END as preparation_duration_valid,
    CASE 
        WHEN delivery.duration IS NOT NULL
        THEN delivery.duration >= INTERVAL '0 seconds' AND delivery.duration <= INTERVAL '30 minutes'
        ELSE true
    END as delivery_duration_valid,
    CASE 
        WHEN o.time_created IS NOT NULL AND o.estimated_delivery_time IS NOT NULL AND
             pending.duration IS NOT NULL AND accept.duration IS NOT NULL AND
             captain_selection.duration IS NOT NULL AND preparing.duration IS NOT NULL AND
             delivery.duration IS NOT NULL
        THEN 
            o.estimated_delivery_time > INTERVAL '0' AND
            pending.duration >= INTERVAL '0 seconds' AND pending.duration <= INTERVAL '30 minutes' AND
            accept.duration >= INTERVAL '0 seconds' AND accept.duration <= INTERVAL '30 minutes' AND
            captain_selection.duration >= INTERVAL '0 seconds' AND captain_selection.duration <= INTERVAL '30 minutes' AND
            preparing.duration >= INTERVAL '0 seconds' AND preparing.duration <= INTERVAL '30 minutes' AND
            delivery.duration >= INTERVAL '0 seconds' AND delivery.duration <= INTERVAL '30 minutes'
        ELSE true
    END as all_validations_passed,
    o.time_created,
    o.estimated_delivery_time,
    pending.duration as pending_duration,
    accept.duration as accept_duration,
    captain_selection.duration as captain_selection_duration,
    preparing.duration as preparation_duration,
    delivery.duration as delivery_duration,
    c.name as customer_name,
    r.name as restaurant_name
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN order_stage_durations pending ON o.order_id = pending.order_id AND pending.stage_name = 'pending'
LEFT JOIN order_stage_durations accept ON o.order_id = accept.order_id AND accept.stage_name = 'accepted'
LEFT JOIN order_stage_durations captain_selection ON o.order_id = captain_selection.order_id AND captain_selection.stage_name = 'captain_selection'
LEFT JOIN order_stage_durations preparing ON o.order_id = preparing.order_id AND preparing.stage_name = 'preparing'
LEFT JOIN order_stage_durations delivery ON o.order_id = delivery.order_id AND delivery.stage_name = 'out_for_delivery'
WHERE o.status IN ('delivered', 'out_for_delivery', 'preparing', 'accepted');

CREATE VIEW order_timestamps_calculated AS
SELECT 
    o.order_id,
    o.status,
    o.time_created,
    o.estimated_delivery_time,
    CASE 
        WHEN pending.duration IS NOT NULL 
        THEN o.time_created + pending.duration
        ELSE NULL 
    END as captain_selection_time,
    CASE 
        WHEN pending.duration IS NOT NULL AND accept.duration IS NOT NULL
        THEN o.time_created + pending.duration + accept.duration
        ELSE NULL 
    END as preparation_start_time,
    CASE 
        WHEN pending.duration IS NOT NULL AND accept.duration IS NOT NULL AND captain_selection.duration IS NOT NULL
        THEN o.time_created + pending.duration + accept.duration + captain_selection.duration
        ELSE NULL 
    END as time_out_of_delivery,
    CASE 
        WHEN pending.duration IS NOT NULL AND accept.duration IS NOT NULL AND captain_selection.duration IS NOT NULL AND preparing.duration IS NOT NULL
        THEN o.time_created + pending.duration + accept.duration + captain_selection.duration + preparing.duration
        ELSE NULL 
    END as time_delivered,
    pending.duration as pending_duration,
    accept.duration as accept_duration,
    captain_selection.duration as captain_selection_duration,
    preparing.duration as preparation_duration,
    delivery.duration as delivery_duration,
    TO_CHAR(
        COALESCE(pending.duration, INTERVAL '0') + 
        COALESCE(accept.duration, INTERVAL '0') + 
        COALESCE(captain_selection.duration, INTERVAL '0') + 
        COALESCE(preparing.duration, INTERVAL '0') + 
        COALESCE(delivery.duration, INTERVAL '0'), 
        'MI:SS'
    ) as total_processing_duration_mmss,
    c.name as customer_name,
    r.name as restaurant_name,
    cap.name as captain_name,
    o.total_price_customer,
    o.delivery_fee,
    o.distance_meters
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id
LEFT JOIN captains cap ON o.captain_id = cap.captain_id
LEFT JOIN order_stage_durations pending ON o.order_id = pending.order_id AND pending.stage_name = 'pending'
LEFT JOIN order_stage_durations accept ON o.order_id = accept.order_id AND accept.stage_name = 'accepted'
LEFT JOIN order_stage_durations captain_selection ON o.order_id = captain_selection.order_id AND captain_selection.stage_name = 'captain_selection'
LEFT JOIN order_stage_durations preparing ON o.order_id = preparing.order_id AND preparing.stage_name = 'preparing'
LEFT JOIN order_stage_durations delivery ON o.order_id = delivery.order_id AND delivery.stage_name = 'out_for_delivery'
WHERE o.status IN ('delivered', 'out_for_delivery', 'preparing', 'accepted');

CREATE OR REPLACE VIEW order_weather_context AS
SELECT
  o.order_id,
  o.time_created,
  r.restaurant_location AS restaurant_city,
  w.recorded_at AS weather_time,
  w.weather_condition,
  w.temperature_celsius,
  w.wind_speed_kmh,
  w.humidity_percent
FROM
  orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
JOIN LATERAL (
  SELECT *
  FROM weather_log w
  WHERE w.city = r.restaurant_location
    AND w.recorded_at <= o.time_created
  ORDER BY w.recorded_at DESC
  LIMIT 1
) w ON true;

-- =============================
-- INDEXES
-- =============================

-- Orders indexes
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX idx_orders_captain_id ON orders(captain_id);
CREATE INDEX idx_orders_time_created ON orders(time_created);
CREATE INDEX idx_orders_estimated_delivery_time ON orders(estimated_delivery_time);
CREATE INDEX idx_orders_delivery_fee ON orders(delivery_fee);
CREATE INDEX idx_orders_distance_meters ON orders(distance_meters);

-- Ratings indexes
CREATE INDEX idx_ratings_restaurant_id ON ratings(restaurant_id);
CREATE INDEX idx_ratings_order_id ON ratings(order_id);
CREATE INDEX idx_ratings_restaurant_score ON ratings(restaurant_emoji_score);
CREATE INDEX idx_ratings_order_score ON ratings(order_emoji_score);

-- Notes indexes
CREATE INDEX idx_notes_target_type ON notes(target_type);
CREATE INDEX idx_notes_reference_id ON notes(reference_id);
CREATE INDEX idx_notes_target_reference ON notes(target_type, reference_id);
CREATE INDEX idx_notes_issue_id ON notes(issue_id);

-- Weather log indexes
CREATE INDEX idx_weather_log_city ON weather_log(city);
CREATE INDEX idx_weather_log_recorded_at ON weather_log(recorded_at);
CREATE INDEX idx_weather_log_city_recorded_at ON weather_log(city, recorded_at);

-- Restaurant phones indexes
CREATE INDEX idx_restaurant_phones_restaurant_id ON restaurant_phones(restaurant_id);
CREATE INDEX idx_restaurant_phones_phone_type ON restaurant_phones(phone_type);

-- Issues indexes
CREATE INDEX idx_issues_order_id ON issues(order_id);
CREATE INDEX idx_issues_customer_id ON issues(customer_id);
CREATE INDEX idx_issues_employee_id ON issues(employee_id);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_category ON issues(category);

-- Call logs indexes
CREATE INDEX idx_call_logs_order_id ON call_logs(order_id);
CREATE INDEX idx_call_logs_customer_id ON call_logs(customer_id);
CREATE INDEX idx_call_logs_issue_id ON call_logs(issue_id);
CREATE INDEX idx_call_logs_employee_id ON call_logs(employee_id);
CREATE INDEX idx_call_logs_call_time ON call_logs(call_time);

-- Employees indexes
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_is_active ON employees(is_active);
CREATE INDEX idx_employees_role ON employees(role);
CREATE INDEX idx_employees_ai_performance_score ON employees(ai_performance_score);
CREATE INDEX idx_employees_efficiency_rating ON employees(efficiency_rating);
CREATE INDEX idx_employees_customer_satisfaction_score ON employees(customer_satisfaction_score);

-- AI Decisions Log indexes
CREATE INDEX idx_ai_decisions_order_id ON ai_decisions_log(order_id);
CREATE INDEX idx_ai_decisions_type ON ai_decisions_log(decision_type);
CREATE INDEX idx_ai_decisions_result ON ai_decisions_log(decision_result);
CREATE INDEX idx_ai_decisions_timestamp ON ai_decisions_log(decision_timestamp);
CREATE INDEX idx_ai_decisions_confidence ON ai_decisions_log(confidence_score);

-- AI Failures indexes
CREATE INDEX idx_ai_failures_order_id ON ai_failures(order_id);
CREATE INDEX idx_ai_failures_module ON ai_failures(failure_module);
CREATE INDEX idx_ai_failures_timestamp ON ai_failures(failure_timestamp);
CREATE INDEX idx_ai_failures_resolved ON ai_failures(is_resolved);
CREATE INDEX idx_ai_failures_severity ON ai_failures(severity_level);

-- Alerts Log indexes
CREATE INDEX idx_alerts_order_id ON alerts_log(order_id);
CREATE INDEX idx_alerts_type ON alerts_log(alert_type);
CREATE INDEX idx_alerts_level ON alerts_log(alert_level);
CREATE INDEX idx_alerts_created_at ON alerts_log(created_at);
CREATE INDEX idx_alerts_resolved ON alerts_log(is_resolved);
CREATE INDEX idx_alerts_resolved_by ON alerts_log(resolved_by);

-- Order Stage Durations indexes
CREATE INDEX idx_stage_durations_order_id ON order_stage_durations(order_id);
CREATE INDEX idx_stage_durations_stage_name ON order_stage_durations(stage_name);
CREATE INDEX idx_stage_durations_start_time ON order_stage_durations(stage_start_time);
--CREATE INDEX idx_stage_durations_status ON order_stage_durations(stage_status);
CREATE INDEX idx_stage_durations_order_stage ON order_stage_durations(order_id, stage_name);

-- Menu items indexes
CREATE INDEX idx_menu_items_restaurant_id ON menu_items(restaurant_id);
CREATE INDEX idx_menu_items_is_visible ON menu_items(is_visible);

-- Menu item options indexes
CREATE INDEX idx_menu_item_options_item_id ON menu_item_options(item_id);
CREATE INDEX idx_menu_item_options_is_available ON menu_item_options(is_available);
CREATE INDEX idx_menu_item_options_item_available ON menu_item_options(item_id, is_available);

-- =============================
-- FUNCTIONS & TRIGGERS
-- =============================

CREATE OR REPLACE FUNCTION handle_scheduled_order()
RETURNS TRIGGER AS $$
DECLARE
    total_required_time INTERVAL;
    restaurant_prep_time INTEGER;
    prep_duration INTERVAL;
    call_restaurant_time TIMESTAMP;
    current_time TIMESTAMP := NOW();
BEGIN
    -- For pick-up orders
    IF NEW.delivery_method = 'pick_up' THEN
        -- Get restaurant preparation time
        SELECT estimated_preparation_time 
        INTO restaurant_prep_time 
        FROM restaurants 
        WHERE restaurant_id = NEW.restaurant_id;
        prep_duration := make_interval(mins => restaurant_prep_time);
        
        -- Calculate when to call restaurant
        IF NEW.estimated_delivery_time IS NOT NULL THEN
            call_restaurant_time := current_time + NEW.estimated_delivery_time - prep_duration;
        END IF;
        
        -- Check if order should be scheduled or processed immediately
        IF NEW.estimated_delivery_time IS NOT NULL AND
           NEW.estimated_delivery_time > (prep_duration + INTERVAL '5 minutes') THEN
            -- Schedule for later
            NEW.status := 'waiting_restaurant_acceptance';
            NEW.call_restaurant_time := call_restaurant_time;
            NEW.is_scheduled := TRUE;
            NEW.select_captain_time := NULL;
        ELSE
            -- Process immediately
            NEW.status := 'processing';
            NEW.is_scheduled := FALSE;
            NEW.call_restaurant_time := NULL;
            NEW.select_captain_time := NULL;
        END IF;
        RETURN NEW;
    END IF;
    
    -- For delivery orders
    SELECT estimated_preparation_time INTO restaurant_prep_time
    FROM restaurants 
    WHERE restaurant_id = NEW.restaurant_id;
    
    total_required_time := make_interval(mins => restaurant_prep_time) 
                          + COALESCE(NEW.expected_delivery_duration, INTERVAL '0') 
                          + INTERVAL '5 minutes';
    
    IF NEW.estimated_delivery_time IS NOT NULL AND 
       NEW.estimated_delivery_time <= total_required_time THEN
        -- Process immediately
        NEW.status := 'processing';
        NEW.is_scheduled := FALSE;
        NEW.call_restaurant_time := current_time;
        NEW.select_captain_time := NULL;
    ELSE
        -- Schedule for later
        NEW.is_scheduled := TRUE;
        NEW.status := 'waiting_restaurant_acceptance';
        IF NEW.estimated_delivery_time IS NOT NULL AND NEW.expected_delivery_duration IS NOT NULL THEN
            NEW.call_restaurant_time := current_time + NEW.estimated_delivery_time - NEW.expected_delivery_duration;
        END IF;
        IF NEW.call_restaurant_time IS NOT NULL THEN
            NEW.select_captain_time := NEW.call_restaurant_time - INTERVAL '15 minutes';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_handle_scheduled_order ON orders;
CREATE TRIGGER trg_handle_scheduled_order
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION handle_scheduled_order();

-- Function & Trigger: تحديث تقييم الموظف عند إغلاق المشكلة
CREATE OR REPLACE FUNCTION update_employee_performance_on_issue_close()
RETURNS TRIGGER AS $$
DECLARE
    v_employee_id INTEGER;
    v_resolution_time INTERVAL;
    v_total_issues INTEGER;
    v_total_resolution_time INTERVAL;
BEGIN
    -- فقط إذا تم إغلاق المشكلة
    IF NEW.status IN ('مغلقة', 'تم الحل', 'closed', 'resolved') AND (OLD.status IS DISTINCT FROM NEW.status) THEN
        v_employee_id := NEW.employee_id;
        IF v_employee_id IS NOT NULL THEN
            -- حساب مدة حل المشكلة
            IF NEW.closed_at IS NOT NULL AND NEW.created_at IS NOT NULL THEN
                v_resolution_time := NEW.closed_at - NEW.created_at;
            ELSE
                v_resolution_time := INTERVAL '0';
            END IF;

            -- تحديث عدد المشاكل المحلولة
            UPDATE employees
            SET total_issues_resolved = COALESCE(total_issues_resolved,0) + 1
            WHERE employee_id = v_employee_id;

            -- تحديث متوسط وقت حل المشكلة
            SELECT total_issues_resolved, avg_issue_resolution_time
            INTO v_total_issues, v_total_resolution_time
            FROM employees WHERE employee_id = v_employee_id;

            IF v_total_issues > 1 THEN
                UPDATE employees
                SET avg_issue_resolution_time = ((COALESCE(v_total_resolution_time, INTERVAL '0') * (v_total_issues - 1)) + v_resolution_time) / v_total_issues
                WHERE employee_id = v_employee_id;
            ELSE
                UPDATE employees
                SET avg_issue_resolution_time = v_resolution_time
                WHERE employee_id = v_employee_id;
            END IF;

            -- تحديث تقييم الكفاءة (مثال: عكس متوسط وقت الحل)
            UPDATE employees
            SET efficiency_rating = ROUND(5.0 - (EXTRACT(EPOCH FROM COALESCE(avg_issue_resolution_time, INTERVAL '0')) / 600), 2) -- كل 10 دقائق = نقطة
            WHERE employee_id = v_employee_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_employee_performance_on_issue_close ON issues;
CREATE TRIGGER trg_update_employee_performance_on_issue_close
    AFTER UPDATE ON issues
    FOR EACH ROW
    EXECUTE FUNCTION update_employee_performance_on_issue_close();

-- Function & Trigger: تحديث عدد الطلبات المسلمة للكابتن عند تسليم الطلب
CREATE OR REPLACE FUNCTION update_captain_delivered_orders()
RETURNS TRIGGER AS $$
DECLARE
    v_captain_id INTEGER;
    v_delivered_count INTEGER;
BEGIN
    -- التحقق من أن الحالة الجديدة هي 'delivered' وأن الحالة القديمة لم تكن 'delivered'
    IF NEW.status = 'delivered' AND (OLD.status IS NULL OR OLD.status != 'delivered') THEN
        v_captain_id := NEW.captain_id;
        
        -- التحقق من وجود كابتن مرتبط بالطلب
        IF v_captain_id IS NOT NULL THEN
            -- حساب عدد الطلبات المسلمة للكابتن (بما في ذلك الطلب الحالي)
            SELECT COUNT(*)
            INTO v_delivered_count
            FROM orders
            WHERE captain_id = v_captain_id AND status = 'delivered';
            
            -- تحديث عدد الطلبات المسلمة في جدول الكباتن
            UPDATE captains
            SET orders_delivered = v_delivered_count
            WHERE captain_id = v_captain_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_captain_delivered_orders ON orders;
CREATE TRIGGER trg_update_captain_delivered_orders
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_captain_delivered_orders();

-- =============================
-- COMMENTS
-- =============================

COMMENT ON TABLE orders IS 'Orders table with core order information. Duration tracking is now handled by the order_stage_durations table for better flexibility and detailed stage analysis.';
COMMENT ON COLUMN orders.time_created IS 'Timestamp when order was created by customer (for analytics)';
COMMENT ON COLUMN orders.estimated_delivery_time IS 'Estimated delivery time calculated at order creation';
COMMENT ON COLUMN orders.distance_meters IS 'Distance between restaurant and customer in meters for delivery fee calculation';
COMMENT ON COLUMN orders.delivery_fee IS 'Captain delivery fee calculated as distance_meters * unit_cost_per_meter (0.001 SAR/meter)';
COMMENT ON COLUMN orders.total_price_customer IS 'Total price charged to customer including delivery fee and restaurant invoice';
COMMENT ON COLUMN orders.total_price_restaurant IS 'Restaurant invoice amount (excluding delivery fee)';
COMMENT ON COLUMN orders.cancel_count_per_day IS 'Number of times customer cancelled orders today';

COMMENT ON TABLE restaurant_phones IS 'Normalized table for restaurant phone numbers. Each phone number is stored as a separate row, allowing unlimited phone numbers per restaurant with proper categorization.';

COMMENT ON TABLE notes IS 'جدول الملاحظات الموحد باستخدام target_type و reference_id لتحديد الكيان المرتبط بالملاحظة. يدعم الملاحظات على العملاء، المطاعم، الكباتن، الطلبات، والمشاكل.';
COMMENT ON COLUMN notes.target_type IS 'نوع الكيان المرتبط بالملاحظة (customer, restaurant, captain, order, issue)';
COMMENT ON COLUMN notes.reference_id IS 'معرف الكيان المرتبط بالملاحظة (customer_id, restaurant_id, captain_id, order_id, issue_id)';
COMMENT ON COLUMN notes.issue_id IS 'معرّف المشكلة المرتبطة بهذه الملاحظة (إن وجدت)';

COMMENT ON TABLE customer_addresses IS 'Enhanced customer addresses with neighborhood and extra details';
COMMENT ON COLUMN customer_addresses.neighborhood IS 'Neighborhood or district within the city';
COMMENT ON COLUMN customer_addresses.extra_details IS 'Additional delivery instructions or landmarks';

COMMENT ON VIEW order_duration_flags IS 'Alert monitoring view for order duration flags - highlights orders exceeding predefined duration thresholds for frontend highlighting. Now uses order_stage_durations table for duration data.';
COMMENT ON VIEW order_duration_analytics IS 'Advanced duration analytics with formatted durations and performance indicators. Now uses order_stage_durations table for duration data.';
COMMENT ON VIEW order_summary IS 'Primary order summary with duration metrics prominently displayed. Now uses order_stage_durations table for duration data.';
COMMENT ON VIEW restaurant_performance IS 'Restaurant performance metrics and ratings using restaurant_emoji_score for accurate restaurant-specific ratings';
COMMENT ON VIEW order_timing_validation IS 'Validation view to check timestamp and duration consistency - use for debugging timing issues. Now uses order_stage_durations table for duration data.';
COMMENT ON VIEW order_timestamps_calculated IS 'Analytics view providing calculated timestamps from durations - use when timestamp analytics are needed. Now uses order_stage_durations table for duration data.';
COMMENT ON VIEW order_weather_context IS 'Joins each order with the most recent weather record from the restaurant''s city before the order''s creation time for contextual analytics.';

COMMENT ON FUNCTION handle_scheduled_order() IS 'Handles scheduled orders and pick-up orders by determining if they should be processed immediately or scheduled for later based on timing requirements';
COMMENT ON TRIGGER trg_handle_scheduled_order ON orders IS 'Automatically handles scheduled order and pick-up order logic before insert - sets appropriate status and timing fields';

COMMENT ON TABLE employees IS 'جدول الموظفين مع حقول تقييم الأداء الشاملة للذكاء الاصطناعي ونظام الأدوار للتحكم في الصلاحيات';
COMMENT ON COLUMN employees.role IS 'دور الموظف في النظام للتحكم في الصلاحيات: admin (مدير) - صلاحيات كاملة، supervisor (مشرف) - صلاحيات إشرافية، staff (موظف) - صلاحيات محدودة';
COMMENT ON COLUMN employees.total_calls_handled IS 'إجمالي عدد المكالمات التي تعامل معها الموظف';
COMMENT ON COLUMN employees.successful_calls IS 'عدد المكالمات الناجحة (تم حل المشكلة)';
COMMENT ON COLUMN employees.failed_calls IS 'عدد المكالمات الفاشلة (لم يتم حل المشكلة)';
COMMENT ON COLUMN employees.avg_call_duration IS 'متوسط مدة المكالمة (لتحليل الكفاءة)';
COMMENT ON COLUMN employees.total_issues_resolved IS 'إجمالي المشاكل التي تم حلها بنجاح';
COMMENT ON COLUMN employees.avg_issue_resolution_time IS 'متوسط الوقت المستغرق لحل المشكلة';
COMMENT ON COLUMN employees.customer_satisfaction_score IS 'درجة رضا العملاء عن الموظف (0-5)';
COMMENT ON COLUMN employees.ai_performance_score IS 'تقييم الذكاء الاصطناعي لأداء الموظف بناءً على تحليل البيانات';
COMMENT ON COLUMN employees.efficiency_rating IS 'تقييم الكفاءة العامة للموظف (مزيج من السرعة والدقة)';
COMMENT ON COLUMN employees.ai_learning_data IS 'بيانات JSON لتعلم الذكاء الاصطناعي (أنماط، تحسينات، توصيات...)';

COMMENT ON TABLE issues IS 'جدول لتتبع مشاكل العملاء/الطلبات مع تصنيف وحالة وسبب وحل كل مشكلة.';
COMMENT ON COLUMN issues.status IS 'حالة المشكلة: مفتوحة/مغلقة/قيد المعالجة...';
COMMENT ON COLUMN issues.category IS 'تصنيف المشكلة (توصيل، جودة، دفع...)';
COMMENT ON COLUMN issues.root_cause IS 'السبب الجذري للمشكلة كما حدده الموظف أو الذكاء الاصطناعي';
COMMENT ON COLUMN issues.resolution IS 'طريقة حل المشكلة';
COMMENT ON COLUMN issues.ai_classification IS 'تصنيف الذكاء الاصطناعي للمشكلة';
COMMENT ON COLUMN issues.employee_note IS 'ملاحظة الموظف النهائية حول المشكلة';

COMMENT ON TABLE call_logs IS 'سجل لجميع المكالمات المتعلقة بالطلبات أو المشاكل أو العملاء مع روابط التسجيلات.';
COMMENT ON COLUMN call_logs.call_recording_url IS 'رابط لتسجيل المكالمة الصوتية (لتحليل الذكاء الاصطناعي لاحقاً)';
COMMENT ON COLUMN call_logs.call_type IS 'نوع المكالمة: وارد/صادر/دعم/تسويق...';

COMMENT ON COLUMN notes.issue_id IS 'معرّف المشكلة المرتبطة بهذه الملاحظة (إن وجدت)';

COMMENT ON FUNCTION update_employee_performance_on_issue_close() IS 'تقوم بتحديث تقييم الموظف تلقائياً عند إغلاق المشكلة (زيادة عدد المشاكل المحلولة، تحديث متوسط وقت الحل، وتقييم الكفاءة)';
COMMENT ON TRIGGER trg_update_employee_performance_on_issue_close ON issues IS 'يعمل تلقائياً بعد تحديث حالة المشكلة إلى مغلقة أو تم الحل.';

COMMENT ON FUNCTION update_captain_delivered_orders() IS 'تقوم بتحديث عدد الطلبات المسلمة للكابتن تلقائياً عند تغيير حالة الطلب إلى delivered. تمنع التحديث المكرر وتتعامل مع الحالات التي لا يوجد فيها كابتن.';
COMMENT ON TRIGGER trg_update_captain_delivered_orders ON orders IS 'يعمل تلقائياً بعد تحديث حالة الطلب إلى delivered لتحديث إحصائيات الكابتن.';

COMMENT ON COLUMN restaurants.price_matches IS 'هل السعر مطابق مع النظام؟ (true/false)';

COMMENT ON TABLE discounts IS 'جدول الحسومات والعروض المرن لدعم جميع أنواع العروض المستقبلية والتكامل مع الذكاء الاصطناعي والتسويق.';
COMMENT ON COLUMN discounts.discount_type IS 'percentage: نسبة مئوية، fixed: مبلغ ثابت، free_delivery: توصيل مجاني، ...';
COMMENT ON COLUMN discounts.value IS 'قيمة الحسم (نسبة أو مبلغ حسب نوع الحسم)';
COMMENT ON COLUMN discounts.code IS 'كود الخصم الذي يدخله العميل (إن وجد)';
COMMENT ON COLUMN discounts.applies_to_delivery IS 'هل ينطبق الحسم على التوصيل فقط؟';
COMMENT ON COLUMN discounts.applies_to_menu_items IS 'هل ينطبق الحسم على أصناف محددة فقط؟';
COMMENT ON COLUMN discounts.applies_to_entire_menu IS 'هل ينطبق الحسم على جميع أصناف المطعم؟';
COMMENT ON COLUMN discounts.restaurant_id IS 'إذا كان غير فارغ، العرض خاص بمطعم معين فقط';
COMMENT ON COLUMN discounts.created_by_ai IS 'هل تم اقتراح العرض من الذكاء الاصطناعي؟ (للاستخدام المستقبلي)';
COMMENT ON COLUMN discounts.ai_recommendation_score IS 'درجة توصية الذكاء الاصطناعي (للاستخدام المستقبلي)';
COMMENT ON COLUMN discounts.min_order_value IS 'الحد الأدنى لقيمة الطلب لتطبيق الحسم (اختياري)';
COMMENT ON COLUMN discounts.usage_limit IS 'الحد الأقصى لعدد مرات استخدام العرض (اختياري)';

COMMENT ON TABLE order_discounts IS 'جدول ربط الحسومات المطبقة فعلياً مع الطلبات. يدعم تطبيق أكثر من حسم على نفس الطلب (عروض مركبة).';

COMMENT ON COLUMN menu_items.discount_percentage IS 'نسبة الحسم المطبقة مباشرة على الصنف (يتم حساب السعر النهائي في الباك اند)';

COMMENT ON TYPE employee_role_enum IS 'نظام أدوار الموظفين للتحكم في الصلاحيات: admin (مدير) - صلاحيات كاملة، supervisor (مشرف) - صلاحيات إشرافية، staff (موظف) - صلاحيات محدودة';

--COMMENT ON TABLE users IS 'جدول المستخدمين الأساسي للنظام مع دعم الأدوار والصلاحيات.';
--COMMENT ON COLUMN users.role IS 'دور المستخدم: customer, captain, restaurant, data_entry, call_center_agent, call_center_supervisor, admin, ai';
--COMMENT ON COLUMN users.device_id IS 'معرف الجهاز لربط الحساب بجهاز محدد (اختياري)';
--COMMENT ON COLUMN customers.user_id IS 'معرف المستخدم المرتبط بهذا العميل (من جدول users)';
--COMMENT ON COLUMN captains.user_id IS 'معرف المستخدم المرتبط بهذا الكابتن (من جدول users)';
--COMMENT ON COLUMN restaurants.user_id IS 'معرف المستخدم المرتبط بهذا المطعم (من جدول users)';


-- =============================
-- AI & ANALYTICS TABLES COMMENTS
-- =============================

COMMENT ON TABLE ai_decisions_log IS 'سجل شامل لجميع قرارات الذكاء الاصطناعي المتعلقة بالطلبات. يستخدم لتحليل أداء الذكاء الاصطناعي وتحسين القرارات المستقبلية.';
COMMENT ON COLUMN ai_decisions_log.decision_type IS 'نوع القرار: reassign_captain (إعادة تعيين كابتن)، cancel_order (إلغاء طلب)، delay_order (تأخير طلب)، optimize_route (تحسين المسار)، etc.';
COMMENT ON COLUMN ai_decisions_log.decision_result IS 'نتيجة القرار: approved (موافق عليه)، denied (مرفوض)، pending (قيد الانتظار)، executed (تم التنفيذ)، failed (فشل)';
COMMENT ON COLUMN ai_decisions_log.ai_model_version IS 'إصدار نموذج الذكاء الاصطناعي المستخدم في اتخاذ القرار (للتتبع والتحسين)';
COMMENT ON COLUMN ai_decisions_log.confidence_score IS 'درجة الثقة في القرار (0-1). كلما زادت الدرجة، زادت ثقة النظام في القرار';
COMMENT ON COLUMN ai_decisions_log.reasoning IS 'شرح منطق القرار بالتفصيل (لماذا تم اتخاذ هذا القرار؟)';
COMMENT ON COLUMN ai_decisions_log.execution_duration IS 'مدة تنفيذ القرار (من وقت اتخاذ القرار حتى تنفيذه)';
COMMENT ON COLUMN ai_decisions_log.affected_entities IS 'الكيانات المتأثرة بالقرار (JSON: captain_id, restaurant_id, customer_id, etc.)';

COMMENT ON TABLE ai_failures IS 'سجل فشل الذكاء الاصطناعي لمراقبة وتحسين أداء النظام. يمكن أن يكون الفشل مرتبط بطلب معين أو عام.';
COMMENT ON COLUMN ai_failures.failure_module IS 'الوحدة التي حدث فيها الفشل: nlp (معالجة اللغة الطبيعية)، call_logic (منطق المكالمات)، route_optimization (تحسين المسار)، etc.';
COMMENT ON COLUMN ai_failures.error_code IS 'كود الخطأ المحدد (للتتبع والتصنيف)';
COMMENT ON COLUMN ai_failures.error_message IS 'رسالة الخطأ التفصيلية (للمطورين والدعم الفني)';
COMMENT ON COLUMN ai_failures.is_resolved IS 'هل تم حل المشكلة؟ (للمتابعة والتحليل)';
COMMENT ON COLUMN ai_failures.resolution_method IS 'طريقة حل المشكلة (manual, automatic, workaround, etc.)';
COMMENT ON COLUMN ai_failures.severity_level IS 'مستوى خطورة الفشل: low (منخفض)، medium (متوسط)، high (عالي)، critical (حرج)';
COMMENT ON COLUMN ai_failures.stack_trace IS 'تفاصيل تقنية للفشل (للمطورين فقط)';

COMMENT ON TABLE alerts_log IS 'سجل التنبيهات المهمة في النظام (تأخير الطلبات، سلوك غير طبيعي، مشاكل النظام). يدعم التصعيد التلقائي واليدوي.';
COMMENT ON COLUMN alerts_log.alert_type IS 'نوع التنبيه: delayed_order (طلب متأخر)، abnormal_behavior (سلوك غير طبيعي)، system_issue (مشكلة نظام)، etc.';
COMMENT ON COLUMN alerts_log.alert_level IS 'مستوى التنبيه: info (معلومات)، warning (تحذير)، error (خطأ)، critical (حرج)';
COMMENT ON COLUMN alerts_log.alert_message IS 'رسالة التنبيه المباشرة للموظفين';
COMMENT ON COLUMN alerts_log.alert_data IS 'بيانات إضافية للتنبيه (JSON: تفاصيل إضافية، سياق، إلخ)';
COMMENT ON COLUMN alerts_log.resolved_by IS 'الموظف الذي حل التنبيه (للمسؤولية والمتابعة)';
COMMENT ON COLUMN alerts_log.auto_resolved IS 'هل تم حل التنبيه تلقائياً؟ (لتحليل كفاءة النظام)';
COMMENT ON COLUMN alerts_log.escalation_level IS 'مستوى التصعيد (0 = لا تصعيد، 1+ = مستويات التصعيد المتتالية)';

COMMENT ON TABLE order_stage_durations IS 'تتبع دقيق لمدة كل مرحلة من مراحل الطلب. يدعم التحليل التفصيلي لأداء كل مرحلة وتحسين العمليات.';
COMMENT ON COLUMN order_stage_durations.stage_name IS 'اسم المرحلة: pending (قيد الانتظار)، accepted (مقبول)، preparing (قيد التحضير)، out_for_delivery (خارج للتوصيل)، delivered (تم التوصيل)';
COMMENT ON COLUMN order_stage_durations.stage_start_time IS 'وقت بداية المرحلة (مطلوب)';
COMMENT ON COLUMN order_stage_durations.stage_end_time IS 'وقت نهاية المرحلة (NULL إذا لم تنته بعد)';
COMMENT ON COLUMN order_stage_durations.duration IS 'مدة المرحلة (يمكن حسابها أو تخزينها مباشرة للتحسين)';
--COMMENT ON COLUMN order_stage_durations.stage_status IS 'حالة المرحلة: active (نشطة)، completed (مكتملة)، skipped (متخطاة)، cancelled (ملغاة)';
COMMENT ON COLUMN order_stage_durations.stage_metadata IS 'بيانات إضافية للمرحلة (JSON: سبب التأخير، ملاحظات، تفاصيل إضافية)';
COMMENT ON COLUMN order_stage_durations.updated_at IS 'آخر تحديث للمرحلة (للتتبع)';

-- =============================
-- SEQUENCE UPDATES
-- =============================
-- Update all sequences to continue from the current maximum ID values
-- This ensures no ID conflicts when inserting new records after manual data insertion

-- Customers sequence
SELECT setval('customers_customer_id_seq', GREATEST((SELECT COALESCE(MAX(customer_id), 0) FROM customers), 1));

-- Customer addresses sequence
SELECT setval('customer_addresses_address_id_seq', GREATEST((SELECT COALESCE(MAX(address_id), 0) FROM customer_addresses), 1));

-- Restaurants sequence
SELECT setval('restaurants_restaurant_id_seq', GREATEST((SELECT COALESCE(MAX(restaurant_id), 0) FROM restaurants), 1));

-- Menu items sequence
SELECT setval('menu_items_item_id_seq', GREATEST((SELECT COALESCE(MAX(item_id), 0) FROM menu_items), 1));

-- Restaurant phones sequence
SELECT setval('restaurant_phones_id_seq', GREATEST((SELECT COALESCE(MAX(id), 0) FROM restaurant_phones), 1));

-- Captains sequence
SELECT setval('captains_captain_id_seq', GREATEST((SELECT COALESCE(MAX(captain_id), 0) FROM captains), 1));

-- Orders sequence
SELECT setval('orders_order_id_seq', GREATEST((SELECT COALESCE(MAX(order_id), 0) FROM orders), 1));

-- Weather log sequence
SELECT setval('weather_log_weather_id_seq', GREATEST((SELECT COALESCE(MAX(weather_id), 0) FROM weather_log), 1));

-- Employees sequence
SELECT setval('employees_employee_id_seq', GREATEST((SELECT COALESCE(MAX(employee_id), 0) FROM employees), 1));

-- Issues sequence
SELECT setval('issues_issue_id_seq', GREATEST((SELECT COALESCE(MAX(issue_id), 0) FROM issues), 1));

-- Call logs sequence
SELECT setval('call_logs_call_id_seq', GREATEST((SELECT COALESCE(MAX(call_id), 0) FROM call_logs), 1));

-- Notes sequence
SELECT setval('notes_note_id_seq', GREATEST((SELECT COALESCE(MAX(note_id), 0) FROM notes), 1));

-- Ratings sequence
SELECT setval('ratings_rating_id_seq', GREATEST((SELECT COALESCE(MAX(rating_id), 0) FROM ratings), 1));

-- Discounts sequence
SELECT setval('discounts_discount_id_seq', GREATEST((SELECT COALESCE(MAX(discount_id), 0) FROM discounts), 1));

-- AI decisions log sequence
SELECT setval('ai_decisions_log_decision_id_seq', GREATEST((SELECT COALESCE(MAX(decision_id), 0) FROM ai_decisions_log), 1));

-- AI failures sequence
SELECT setval('ai_failures_failure_id_seq', GREATEST((SELECT COALESCE(MAX(failure_id), 0) FROM ai_failures), 1));

-- Alerts log sequence
SELECT setval('alerts_log_alert_id_seq', GREATEST((SELECT COALESCE(MAX(alert_id), 0) FROM alerts_log), 1));

-- Order stage durations sequence
SELECT setval('order_stage_durations_stage_duration_id_seq', GREATEST((SELECT COALESCE(MAX(stage_duration_id), 0) FROM order_stage_durations), 1));

-- Menu item options sequence
SELECT setval('menu_item_options_id_seq', GREATEST((SELECT COALESCE(MAX(id), 0) FROM menu_item_options), 1));

-- Function & Trigger: التحقق من صحة مراجع الملاحظات
CREATE OR REPLACE FUNCTION validate_note_references()
RETURNS TRIGGER AS $$
DECLARE
    v_entity_exists BOOLEAN := FALSE;
BEGIN
    -- التحقق من نوع الملاحظة والمرجع المطلوب
    CASE NEW.target_type
        WHEN 'captain' THEN
            -- التحقق من وجود الكابتن
            SELECT EXISTS(SELECT 1 FROM captains WHERE captain_id = NEW.reference_id)
            INTO v_entity_exists;
            
            IF NOT v_entity_exists THEN
                RAISE EXCEPTION 'هذا الكابتن مو موجود' USING ERRCODE = '23503';
            END IF;
            
        WHEN 'customer' THEN
            -- التحقق من وجود العميل
            SELECT EXISTS(SELECT 1 FROM customers WHERE customer_id = NEW.reference_id)
            INTO v_entity_exists;
            
            IF NOT v_entity_exists THEN
                RAISE EXCEPTION 'هذا العميل مو موجود' USING ERRCODE = '23503';
            END IF;
            
        WHEN 'restaurant' THEN
            -- التحقق من وجود المطعم
            SELECT EXISTS(SELECT 1 FROM restaurants WHERE restaurant_id = NEW.reference_id)
            INTO v_entity_exists;
            
            IF NOT v_entity_exists THEN
                RAISE EXCEPTION 'هذا المطعم مو موجود' USING ERRCODE = '23503';
            END IF;
            
        WHEN 'order' THEN
            -- التحقق من وجود الطلب
            SELECT EXISTS(SELECT 1 FROM orders WHERE order_id = NEW.reference_id)
            INTO v_entity_exists;
            
            IF NOT v_entity_exists THEN
                RAISE EXCEPTION 'هذا الطلب مو موجود' USING ERRCODE = '23503';
            END IF;
            
        WHEN 'issue' THEN
            -- التحقق من وجود المشكلة
            SELECT EXISTS(SELECT 1 FROM issues WHERE issue_id = NEW.reference_id)
            INTO v_entity_exists;
            
            IF NOT v_entity_exists THEN
                RAISE EXCEPTION 'هذه المشكلة مو موجودة' USING ERRCODE = '23503';
            END IF;
            
        ELSE
            -- نوع ملاحظة غير معروف
            RAISE EXCEPTION 'نوع الملاحظة غير صحيح' USING ERRCODE = '22P02';
    END CASE;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_note_references ON notes;
CREATE TRIGGER trg_validate_note_references
    BEFORE INSERT OR UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION validate_note_references();

COMMENT ON FUNCTION validate_note_references() IS 'تتحقق من صحة مراجع الملاحظات قبل الإدخال أو التحديث. تضمن أن الملاحظات تشير دائماً إلى كيانات موجودة فعلياً في النظام (كباتن، عملاء، مطاعم، طلبات) باستخدام البنية الموحدة target_type و reference_id.';
COMMENT ON TRIGGER trg_validate_note_references ON notes IS 'يعمل تلقائياً قبل إدخال أو تحديث الملاحظات للتحقق من صحة المراجع. يرفض الإدخال إذا كان المرجع غير موجود.';

COMMENT ON TABLE ratings IS 'جدول التقييمات مع تعليقات منفصلة للمطاعم والطلبات. يدعم تقييم المطعم أو الطلب مع تعليق خاص بكل منهما.';
COMMENT ON COLUMN ratings.restaurant_comment IS 'تعليق العميل على المطعم (الطعام، الخدمة، الجودة...) - يستخدم فقط عند تقييم المطعم';
COMMENT ON COLUMN ratings.order_comment IS 'تعليق العميل على الطلب (التوصيل، السرعة، الكابتن...) - يستخدم فقط عند تقييم الطلب';
COMMENT ON COLUMN ratings.restaurant_emoji_score IS 'تقييم المطعم بالرموز التعبيرية (1-5) - 1 سيء جداً، 5 ممتاز';
COMMENT ON COLUMN ratings.order_emoji_score IS 'تقييم الطلب بالرموز التعبيرية (1-5) - 1 سيء جداً، 5 ممتاز';

COMMENT ON TABLE menu_item_options IS 'جدول إضافات الأصناف - يحتوي على جميع الإضافات المتاحة لكل صنف (زيادة جبنة، صوص حار، إلخ). يتم استخدامه لسحب الإضافات تلقائياً في الواجهة.';
COMMENT ON COLUMN menu_item_options.item_id IS 'معرف الصنف المرتبط بهذه الإضافة (مرتبط بجدول menu_items.item_id)';
COMMENT ON COLUMN menu_item_options.name IS 'اسم الإضافة (مثل: زيادة جبنة، صوص حار، بطاطس إضافية)';
COMMENT ON COLUMN menu_item_options.price IS 'سعر الإضافة بالريال السعودي';
COMMENT ON COLUMN menu_item_options.is_available IS 'هل الإضافة متاحة حالياً؟ (يمكن إخفاؤها مؤقتاً)';
COMMENT ON COLUMN menu_item_options.created_at IS 'تاريخ إنشاء الإضافة';

COMMENT ON TABLE menu_items IS 'جدول أصناف القوائم مع دعم الإضافات عبر JSONB وخصم النسب المئوية. الإضافات التفصيلية محفوظة في جدول menu_item_options.';
COMMENT ON COLUMN menu_items.extras IS 'إضافات الصنف بتنسيق JSON (للتوافق مع النظام القديم). الإضافات التفصيلية محفوظة في جدول menu_item_options.';

-- Menu Items with Options View - عرض الأصناف مع إضافاتها
CREATE VIEW menu_items_with_options AS
SELECT 
    mi.item_id,
    mi.restaurant_id,
    mi.name_item,
    mi.price,
    mi.discount_percentage,
    mi.is_visible,
    mi.extras as legacy_extras, -- الإضافات القديمة (للتوافق)
    -- تجميع الإضافات الجديدة في JSON
    COALESCE(
        json_agg(
            json_build_object(
                'id', mio.id,
                'name', mio.name,
                'price', mio.price,
                'is_available', mio.is_available
            ) ORDER BY mio.name
        ) FILTER (WHERE mio.id IS NOT NULL),
        '[]'::json
    ) as available_options
FROM menu_items mi
LEFT JOIN menu_item_options mio ON mi.item_id = mio.item_id AND mio.is_available = true
WHERE mi.is_visible = true
GROUP BY mi.item_id, mi.restaurant_id, mi.name_item, mi.price, mi.discount_percentage, mi.is_visible, mi.extras;

COMMENT ON VIEW menu_items_with_options IS 'عرض شامل للأصناف مع إضافاتها المتاحة. يستخدم للواجهة الأمامية لعرض الأصناف مع خيارات الإضافات تلقائياً. يدعم الإضافات الجديدة من جدول menu_item_options والإضافات القديمة من عمود extras.';