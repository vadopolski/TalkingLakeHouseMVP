-- Initialize Analytics Database with Sample Data

-- Create sales_transactions table
CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_date DATE NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    revenue DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create website_visits table (for future user stories)
CREATE TABLE IF NOT EXISTS website_visits (
    visit_id SERIAL PRIMARY KEY,
    visit_date DATE NOT NULL,
    visit_hour INTEGER NOT NULL,
    visitor_source VARCHAR(100),
    page_views INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample sales data for the last 60 days
INSERT INTO sales_transactions (transaction_date, product_id, product_name, revenue, quantity)
VALUES
    -- Last 7 days - recent sales
    (CURRENT_DATE - INTERVAL '1 day', 'PROD-001', 'Laptop Pro 15', 1299.99, 2),
    (CURRENT_DATE - INTERVAL '1 day', 'PROD-002', 'Wireless Mouse', 29.99, 5),
    (CURRENT_DATE - INTERVAL '1 day', 'PROD-003', 'USB-C Hub', 49.99, 3),
    (CURRENT_DATE - INTERVAL '2 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 1),
    (CURRENT_DATE - INTERVAL '2 days', 'PROD-004', 'Mechanical Keyboard', 149.99, 2),
    (CURRENT_DATE - INTERVAL '3 days', 'PROD-002', 'Wireless Mouse', 29.99, 8),
    (CURRENT_DATE - INTERVAL '3 days', 'PROD-005', 'Monitor 27"', 399.99, 2),
    (CURRENT_DATE - INTERVAL '4 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 3),
    (CURRENT_DATE - INTERVAL '4 days', 'PROD-003', 'USB-C Hub', 49.99, 4),
    (CURRENT_DATE - INTERVAL '5 days', 'PROD-006', 'Webcam HD', 89.99, 6),
    (CURRENT_DATE - INTERVAL '6 days', 'PROD-004', 'Mechanical Keyboard', 149.99, 3),
    (CURRENT_DATE - INTERVAL '7 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 2),

    -- Last 30 days - monthly sales
    (CURRENT_DATE - INTERVAL '8 days', 'PROD-002', 'Wireless Mouse', 29.99, 10),
    (CURRENT_DATE - INTERVAL '9 days', 'PROD-005', 'Monitor 27"', 399.99, 3),
    (CURRENT_DATE - INTERVAL '10 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 4),
    (CURRENT_DATE - INTERVAL '12 days', 'PROD-003', 'USB-C Hub', 49.99, 7),
    (CURRENT_DATE - INTERVAL '14 days', 'PROD-006', 'Webcam HD', 89.99, 5),
    (CURRENT_DATE - INTERVAL '15 days', 'PROD-004', 'Mechanical Keyboard', 149.99, 4),
    (CURRENT_DATE - INTERVAL '18 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 2),
    (CURRENT_DATE - INTERVAL '20 days', 'PROD-002', 'Wireless Mouse', 29.99, 12),
    (CURRENT_DATE - INTERVAL '22 days', 'PROD-005', 'Monitor 27"', 399.99, 2),
    (CURRENT_DATE - INTERVAL '25 days', 'PROD-003', 'USB-C Hub', 49.99, 6),
    (CURRENT_DATE - INTERVAL '28 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 5),

    -- Older data (30-60 days ago)
    (CURRENT_DATE - INTERVAL '32 days', 'PROD-002', 'Wireless Mouse', 29.99, 15),
    (CURRENT_DATE - INTERVAL '35 days', 'PROD-006', 'Webcam HD', 89.99, 8),
    (CURRENT_DATE - INTERVAL '38 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 3),
    (CURRENT_DATE - INTERVAL '40 days', 'PROD-004', 'Mechanical Keyboard', 149.99, 5),
    (CURRENT_DATE - INTERVAL '45 days', 'PROD-005', 'Monitor 27"', 399.99, 4),
    (CURRENT_DATE - INTERVAL '50 days', 'PROD-003', 'USB-C Hub', 49.99, 10),
    (CURRENT_DATE - INTERVAL '55 days', 'PROD-001', 'Laptop Pro 15', 1299.99, 2),
    (CURRENT_DATE - INTERVAL '60 days', 'PROD-002', 'Wireless Mouse', 29.99, 20);

-- Insert sample website visit data (for future user stories)
INSERT INTO website_visits (visit_date, visit_hour, visitor_source, page_views)
VALUES
    (CURRENT_DATE - INTERVAL '1 day', 9, 'Google Search', 150),
    (CURRENT_DATE - INTERVAL '1 day', 14, 'Direct', 200),
    (CURRENT_DATE - INTERVAL '1 day', 18, 'Social Media', 180),
    (CURRENT_DATE - INTERVAL '2 days', 10, 'Google Search', 160),
    (CURRENT_DATE - INTERVAL '2 days', 15, 'Email Campaign', 120),
    (CURRENT_DATE - INTERVAL '3 days', 11, 'Direct', 190),
    (CURRENT_DATE - INTERVAL '3 days', 16, 'Social Media', 210);

-- Create read-only user for application access
CREATE USER readonly_user WITH PASSWORD 'readonly123';
GRANT CONNECT ON DATABASE analytics_db TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON sales_transactions TO readonly_user;
GRANT SELECT ON website_visits TO readonly_user;

-- Verify data
SELECT 'Sales Transactions Count: ' || COUNT(*) FROM sales_transactions;
SELECT 'Website Visits Count: ' || COUNT(*) FROM website_visits;
