DROP TABLE IF EXISTS order_ratings CASCADE;
DROP TABLE IF EXISTS order_notes CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS captains CASCADE;
DROP TABLE IF EXISTS menu_items CASCADE;
DROP TABLE IF EXISTS restaurants CASCADE;
DROP TABLE IF EXISTS customer_addresses CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

DROP TYPE IF EXISTS membership_type_enum CASCADE;
DROP TYPE IF EXISTS restaurant_status_enum CASCADE;
DROP TYPE IF EXISTS restaurant_availability_enum CASCADE;
DROP TYPE IF EXISTS order_status_enum CASCADE;
DROP TYPE IF EXISTS address_type_enum CASCADE;

-- Create enum types
CREATE TYPE membership_type_enum AS ENUM ('normal', 'vip', 'movo_plus');
CREATE TYPE restaurant_status_enum AS ENUM ('online', 'offline');
CREATE TYPE restaurant_availability_enum AS ENUM ('available', 'busy');
CREATE TYPE order_status_enum AS ENUM ('pending', 'accepted', 'preparing', 'out_for_delivery', 'delivered', 'cancelled');
CREATE TYPE address_type_enum AS ENUM ('home', 'work', 'other');

-- Create customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    membership_type membership_type_enum DEFAULT 'normal'
);

-- Create customer_addresses table
CREATE TABLE customer_addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    address_type address_type_enum DEFAULT 'home',
    city VARCHAR(100) NOT NULL,
    street VARCHAR(200) NOT NULL,
    district VARCHAR(100),
    neighborhood VARCHAR(100),
    additional_details TEXT,
    extra_details TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_default BOOLEAN DEFAULT false
);

-- Create restaurants table
CREATE TABLE restaurants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    delivery_time INTEGER NOT NULL, -- in minutes
    status restaurant_status_enum DEFAULT 'offline',
    availability restaurant_availability_enum DEFAULT 'available'
);

-- Create menu_items table
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    restaurant_id INTEGER REFERENCES restaurants(id),
    name_item VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    extras TEXT
);

-- Create captains table
CREATE TABLE captains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    orders_delivered INTEGER DEFAULT 0,
    performance DECIMAL(3, 2) DEFAULT 5.00, -- Rating out of 5
    available BOOLEAN DEFAULT true
);

-- Create orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    restaurant_id INTEGER REFERENCES restaurants(id),
    assigned_captain INTEGER REFERENCES captains(id),
    status order_status_enum DEFAULT 'pending',
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_pending TIMESTAMP,
    time_out_of_delivery TIMESTAMP,
    time_delivered TIMESTAMP,
    issue TEXT,
    order_note TEXT
);

-- Create order_notes table
CREATE TABLE order_notes (
    order_id INTEGER REFERENCES orders(order_id),
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, created_at)
);

-- Create order_ratings table
CREATE TABLE order_ratings (
    order_id INTEGER PRIMARY KEY REFERENCES orders(order_id),
    customer_rating_of_delivery INTEGER CHECK (customer_rating_of_delivery BETWEEN 1 AND 5),
    customer_rating_of_restaurant INTEGER CHECK (customer_rating_of_restaurant BETWEEN 1 AND 5),
    comment TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data for customers
INSERT INTO customers (name, phone, latitude, longitude, membership_type)
SELECT 
    'Customer ' || i,
    '+1' || LPAD(FLOOR(RANDOM() * 1000000000)::TEXT, 10, '0'),
    24.7136 + (RANDOM() * 2), -- Riyadh latitude range
    46.6753 + (RANDOM() * 2), -- Riyadh longitude range
    (ARRAY['normal', 'vip', 'movo_plus'])[FLOOR(RANDOM() * 3 + 1)]::membership_type_enum
FROM generate_series(1, 200) i;

-- Insert sample data for customer_addresses
INSERT INTO customer_addresses (customer_id, address_type, city, street, district, neighborhood, additional_details, latitude, longitude, is_default)
SELECT 
    i,
    (ARRAY['home', 'work', 'other'])[FLOOR(RANDOM() * 3 + 1)]::address_type_enum,
    'City ' || FLOOR(RANDOM() * 5 + 1),
    'Street ' || FLOOR(RANDOM() * 100 + 1),
    'District ' || FLOOR(RANDOM() * 10 + 1),
    'Neighborhood ' || FLOOR(RANDOM() * 20 + 1),
    CASE WHEN RANDOM() > 0.7 THEN 'Additional details for delivery' ELSE NULL END,
    24.7136 + (RANDOM() * 2),
    46.6753 + (RANDOM() * 2),
    CASE WHEN i % 3 = 0 THEN true ELSE false END
FROM generate_series(1, 200) i;

-- Insert sample data for restaurants
INSERT INTO restaurants (name, phone, latitude, longitude, delivery_time, status, availability)
SELECT 
    'Restaurant ' || i,
    '+966' || LPAD(FLOOR(RANDOM() * 100000000)::TEXT, 8, '0'),
    24.7136 + (RANDOM() * 2),
    46.6753 + (RANDOM() * 2),
    FLOOR(RANDOM() * 45 + 15)::INTEGER, -- 15-60 minutes delivery time
    (ARRAY['online', 'offline'])[FLOOR(RANDOM() * 2 + 1)]::restaurant_status_enum,
    (ARRAY['available', 'busy'])[FLOOR(RANDOM() * 2 + 1)]::restaurant_availability_enum
FROM generate_series(1, 50) i;

-- Insert sample data for menu_items
INSERT INTO menu_items (restaurant_id, name_item, price, extras)
SELECT 
    FLOOR(RANDOM() * 50 + 1),
    'Menu Item ' || i,
    ROUND((RANDOM() * 100 + 10)::numeric, 2),
    CASE WHEN RANDOM() > 0.5 THEN 'Extra options available' ELSE NULL END
FROM generate_series(1, 200) i;

-- Insert sample data for captains
INSERT INTO captains (name, phone, vehicle_type, orders_delivered, performance, available)
SELECT 
    'Captain ' || i,
    '+966' || LPAD(FLOOR(RANDOM() * 100000000)::TEXT, 8, '0'),
    (ARRAY['Motorcycle', 'Car', 'Bicycle'])[FLOOR(RANDOM() * 3 + 1)],
    FLOOR(RANDOM() * 1000),
    ROUND((RANDOM() * 2 + 3)::numeric, 2), -- Rating between 3.00 and 5.00
    RANDOM() > 0.2 -- 80% chance of being available
FROM generate_series(1, 50) i;

-- Insert sample data for orders
INSERT INTO orders (customer_id, restaurant_id, assigned_captain, status, time_created, time_pending, time_out_of_delivery, time_delivered)
SELECT 
    FLOOR(RANDOM() * 200 + 1),
    FLOOR(RANDOM() * 50 + 1),
    FLOOR(RANDOM() * 50 + 1),
    (ARRAY['pending', 'accepted', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'])[FLOOR(RANDOM() * 6 + 1)]::order_status_enum,
    NOW() - (INTERVAL '1 day' * RANDOM() * 30),
    CASE WHEN RANDOM() > 0.5 THEN NOW() - (INTERVAL '1 hour' * RANDOM() * 24) ELSE NULL END,
    CASE WHEN RANDOM() > 0.5 THEN NOW() - (INTERVAL '30 minutes' * RANDOM() * 48) ELSE NULL END,
    CASE WHEN RANDOM() > 0.5 THEN NOW() - (INTERVAL '15 minutes' * RANDOM() * 96) ELSE NULL END
FROM generate_series(1, 200) i;

-- Insert sample data for order_notes
INSERT INTO order_notes (order_id, note_text, created_at)
SELECT 
    FLOOR(RANDOM() * 200 + 1),
    (ARRAY['Leave at the door', 'Call when outside', 'Extra napkins please', 'No utensils needed', 'Please deliver to reception', 'Ring doorbell twice', 'Leave with security guard', 'Call upon arrival', 'No contact delivery', 'Extra sauce packets please'])[FLOOR(RANDOM() * 10 + 1)],
    NOW() - (INTERVAL '1 day' * RANDOM() * 30) - (INTERVAL '1 hour' * RANDOM() * 24) - (INTERVAL '1 minute' * RANDOM() * 60)
FROM generate_series(1, 200) i;

-- Insert sample data for order_ratings
INSERT INTO order_ratings (order_id, customer_rating_of_delivery, customer_rating_of_restaurant, comment)
SELECT 
    i,
    FLOOR(RANDOM() * 5 + 1),
    FLOOR(RANDOM() * 5 + 1),
    CASE 
        WHEN RANDOM() > 0.7 THEN 'Great service!'
        WHEN RANDOM() > 0.4 THEN 'Good experience'
        ELSE 'Could be better'
    END
FROM generate_series(1, 150) i;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_membership ON customers(membership_type);
CREATE INDEX IF NOT EXISTS idx_customer_addresses_customer ON customer_addresses(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_addresses_type ON customer_addresses(address_type);
CREATE INDEX IF NOT EXISTS idx_customer_addresses_location ON customer_addresses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_restaurants_status ON restaurants(status);
CREATE INDEX IF NOT EXISTS idx_restaurants_availability ON restaurants(availability);
CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant ON menu_items(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_captains_available ON captains(available) WHERE available = true;
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(time_created);

-- Add comments for documentation
COMMENT ON TABLE customers IS 'Customer information with membership types';
COMMENT ON TABLE customer_addresses IS 'Customer addresses with full details and geolocation';
COMMENT ON TABLE restaurants IS 'Restaurant information with delivery settings';
COMMENT ON TABLE menu_items IS 'Restaurant menu items with pricing';
COMMENT ON TABLE captains IS 'Delivery captains with performance tracking';
COMMENT ON TABLE orders IS 'Order tracking with status and timing';
COMMENT ON TABLE order_notes IS 'Additional notes for orders';
COMMENT ON TABLE order_ratings IS 'Customer ratings for orders and delivery';
