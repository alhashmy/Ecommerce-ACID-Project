DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- 1. جدول المنتجات المطور مع الأقسام والخصومات
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL, -- الأقسام: Laptops, Phones, Accessories
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0),
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    image_url TEXT NOT NULL,
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00 CHECK (discount_percentage >= 0 AND discount_percentage <= 100)
);

-- 2. جدول الطلبات المطور ليشمل حالات الشحن وكود الخصم
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_address TEXT NOT NULL,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    total_price NUMERIC(10, 2) NOT NULL,
    promo_code VARCHAR(20) DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- الحالات: Pending, Approved, In Transit, Delivered, Rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 🛍️ تغذية النظام بـ 30 منتجاً إلكترونياً (10 لكل قسم)
-- قسم اللابتوبات (Laptops)
INSERT INTO products (product_name, category, price, stock_quantity, image_url) VALUES
('Asus ROG Strix G16', 'Laptops', 1450.00, 5, 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500'),
('MacBook Air M3', 'Laptops', 1199.00, 7, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'),
('Dell XPS 15', 'Laptops', 1699.00, 3, 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500'),
('HP Pavilion 15', 'Laptops', 650.00, 12, 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500'),
('Lenovo Legion 5', 'Laptops', 1050.00, 4, 'https://images.unsplash.com/photo-1625457672252-c77a7603af29?w=500'),
('Acer Nitro V', 'Laptops', 799.00, 8, 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500'),
('MSI Cyborg 15', 'Laptops', 950.00, 3, 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=500'),
('Huawei MateBook D16', 'Laptops', 720.00, 10, 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=500'),
('Gigabyte G5 Gaming', 'Laptops', 880.00, 6, 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500'),
('Apple MacBook Pro 16', 'Laptops', 2499.00, 2, 'https://images.unsplash.com/photo-1542393545-10f5cde2c810?w=500');

-- قسم الهواتف والصوتيات (Phones)
INSERT INTO products (product_name, category, price, stock_quantity, image_url) VALUES
('iPhone 15 Pro Max', 'Phones', 1250.00, 8, 'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500'),
('Samsung Galaxy S24 Ultra', 'Phones', 1180.00, 6, 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500'),
('Google Pixel 8 Pro', 'Phones', 999.00, 5, 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500'),
('Xiaomi 14 Ultra', 'Phones', 920.00, 4, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500'),
('AirPods Pro 2', 'Phones', 249.00, 25, 'https://images.unsplash.com/photo-1588444837495-c6cfeb53f32d?w=500'),
('Sony WH-1000XM5', 'Phones', 349.00, 12, 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500'),
('OnePlus 12', 'Phones', 799.00, 7, 'https://images.unsplash.com/photo-1565630916779-e303be97b6f5?w=500'),
('Nothing Phone 2', 'Phones', 599.00, 9, 'https://images.unsplash.com/photo-1573148195900-7845dcb9b127?w=500'),
('Beats Studio Headphones', 'Phones', 199.00, 15, 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=500'),
('Samsung Galaxy Buds 3', 'Phones', 179.00, 20, 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500');

-- قسم الملحقات والألعاب (Accessories)
INSERT INTO products (product_name, category, price, stock_quantity, image_url) VALUES
('Logitech G Pro X Superlight', 'Accessories', 139.00, 15, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500'),
('Razer BlackWidow V4', 'Accessories', 169.00, 10, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500'),
('PS5 DualSense Edge', 'Accessories', 199.00, 8, 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=500'),
('HyperX QuadCast S', 'Accessories', 159.00, 14, 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500'),
('Samsung Odyssey G7 32"', 'Accessories', 699.00, 4, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500'),
('Corsair Commander Pro', 'Accessories', 74.00, 20, 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=500'),
('Elgato Stream Deck MK.2', 'Accessories', 149.00, 11, 'https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=500'),
('Asus ROG Harpe Ace Mouse', 'Accessories', 119.00, 2, 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500'),
('SteelSeries Arctis Nova 7', 'Accessories', 179.00, 9, 'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=500'),
('Kingston FURY Renegade 32GB', 'Accessories', 125.00, 30, 'https://images.unsplash.com/photo-1562976540-1502c2145186?w=500');