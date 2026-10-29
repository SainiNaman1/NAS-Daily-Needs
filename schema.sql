-- ========================================================
-- Database Schema for NAS Daily Needs Counter & Inventory
-- ========================================================

CREATE DATABASE IF NOT EXISTS counter;
USE counter;

-- Table: products (with inventory stock tracking)
CREATE TABLE IF NOT EXISTS products (
    PID VARCHAR(10) PRIMARY KEY,
    PName VARCHAR(50) NOT NULL,
    Price FLOAT NOT NULL,
    stock INT NOT NULL DEFAULT 50
);

-- Table: buyer (customer directory)
CREATE TABLE IF NOT EXISTS buyer (
    mobile BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL
);

-- Table: bill (invoice summary header)
CREATE TABLE IF NOT EXISTS bill (
    BillNo INT PRIMARY KEY,
    mobile BIGINT NOT NULL,
    `date` DATE NOT NULL,
    mode VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    total FLOAT NOT NULL
);

-- Table: bill_items (itemized line items for each bill)
CREATE TABLE IF NOT EXISTS bill_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    BillNo INT NOT NULL,
    PID VARCHAR(10) NOT NULL,
    PName VARCHAR(50) NOT NULL,
    price FLOAT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    item_total FLOAT NOT NULL,
    INDEX (BillNo)
);

-- ========================================================
-- Initial Sample Records
-- ========================================================

-- Sample Products
INSERT INTO products (PID, PName, Price, stock) VALUES
('P001', 'Sugar 1kg', 23.00, 45),
('P002', 'Amul Milk 500ml', 33.00, 20),
('P003', 'Brown Bread', 40.00, 15),
('P004', 'Fortune Oil 1L', 145.00, 30),
('P005', 'Tata Salt 1kg', 28.00, 50),
('P006', 'Aashirvaad Atta 5kg', 240.00, 25),
('P007', 'Basmati Rice 1kg', 95.00, 35),
('P008', 'Dettol Soap', 35.00, 40),
('P009', 'Colgate Paste', 65.00, 30),
('P010', 'Tata Tea Gold 250g', 130.00, 18),
('2', 'Maggi Noodles', 12.00, 60)
ON DUPLICATE KEY UPDATE PName = VALUES(PName), Price = VALUES(Price), stock = VALUES(stock);

-- Sample Customers
INSERT INTO buyer (mobile, name, address) VALUES
(9876543210, 'Aman Verma', 'Flat 402, Green Park, Delhi'),
(9812345678, 'Priya Sharma', 'House 12, Sector 15, Noida'),
(9898989898, 'Rohit Gupta', 'A-45, Model Town, Delhi'),
(9765432109, 'Neha Patel', 'Block C, Rajouri Garden, Delhi'),
(9654321870, 'Vikram Singh', '34/B, Civil Lines, Gurgaon')
ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address);

-- Sample Bills
INSERT INTO bill (BillNo, mobile, `date`, mode, status, total) VALUES
(101, 9876543210, '2026-10-25', 'UPI', 'Paid', 273.00),
(102, 9812345678, '2026-10-26', 'Cash', 'Paid', 73.00),
(103, 9898989898, '2026-10-27', 'Card', 'Paid', 335.00),
(104, 9765432109, '2026-10-28', 'PayLater', 'Pending', 145.00),
(105, 9876543210, '2026-10-28', 'UPI', 'Paid', 170.00)
ON DUPLICATE KEY UPDATE total = VALUES(total);

-- Sample Itemized Bill Records
INSERT INTO bill_items (BillNo, PID, PName, price, quantity, item_total) VALUES
(101, 'P004', 'Fortune Oil 1L', 145.0, 1, 145.0),
(101, 'P007', 'Basmati Rice 1kg', 95.0, 1, 95.0),
(101, 'P002', 'Amul Milk 500ml', 33.0, 1, 33.0),
(102, 'P003', 'Brown Bread', 40.0, 1, 40.0),
(102, 'P002', 'Amul Milk 500ml', 33.0, 1, 33.0),
(103, 'P006', 'Aashirvaad Atta 5kg', 240.0, 1, 240.0),
(103, 'P007', 'Basmati Rice 1kg', 95.0, 1, 95.0),
(104, 'P004', 'Fortune Oil 1L', 145.0, 1, 145.0),
(105, 'P010', 'Tata Tea Gold 250g', 130.0, 1, 130.0),
(105, 'P003', 'Brown Bread', 40.0, 1, 40.0);
