import os
from datetime import date, timedelta
import mysql.connector as n1
from mysql.connector import Error

DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "saini")
DB_NAME = os.getenv("MYSQL_DATABASE", "counter")


def get_connection():
    """Create and return a MySQL connection with autocommit."""
    try:
        conn = n1.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASS,
            database=DB_NAME,
            autocommit=True
        )
        return conn
    except Error as err:
        print(f"Database Connection Error: {err}")
        return None


def init_db():
    """Ensure database and all required tables exist."""
    try:
        conn = n1.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cur.execute(f"USE `{DB_NAME}`")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            PID VARCHAR(10) PRIMARY KEY,
            PName VARCHAR(50) NOT NULL,
            Price FLOAT NOT NULL,
            stock INT NOT NULL DEFAULT 50
        )
        """)

        # Add stock if missing on older schema
        cur.execute("SHOW COLUMNS FROM products LIKE 'stock'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE products ADD COLUMN stock INT NOT NULL DEFAULT 50")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS buyer (
            mobile BIGINT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            address VARCHAR(255) NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS bill (
            BillNo INT PRIMARY KEY,
            mobile BIGINT NOT NULL,
            `date` DATE NOT NULL,
            mode VARCHAR(30) NOT NULL,
            status VARCHAR(30) NOT NULL,
            total FLOAT NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            BillNo INT NOT NULL,
            PID VARCHAR(10) NOT NULL,
            PName VARCHAR(50) NOT NULL,
            price FLOAT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            item_total FLOAT NOT NULL,
            INDEX (BillNo)
        )
        """)

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error as err:
        print(f"Init DB Error: {err}")
        return False


# ---------------------------------------------
# Products & Inventory Queries
# ---------------------------------------------
def get_all_products(search_term=""):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    if search_term:
        term = f"%{search_term}%"
        cur.execute("""
            SELECT PID, PName, Price, stock 
            FROM products 
            WHERE PID LIKE %s OR PName LIKE %s 
            ORDER BY PName
        """, (term, term))
    else:
        cur.execute("SELECT PID, PName, Price, stock FROM products ORDER BY PName")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def add_product(pid, name, price, stock):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO products (PID, PName, Price, stock) VALUES (%s, %s, %s, %s)",
                    (pid, name, price, stock))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Product added successfully"
    except Error as err:
        cur.close()
        conn.close()
        return False, str(err)


def update_product(pid, name, price, stock):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    cur = conn.cursor()
    try:
        cur.execute("UPDATE products SET PName=%s, Price=%s, stock=%s WHERE PID=%s",
                    (name, price, stock, pid))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Product updated successfully"
    except Error as err:
        cur.close()
        conn.close()
        return False, str(err)


def delete_product(pid):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM products WHERE PID=%s", (pid,))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Product deleted successfully"
    except Error as err:
        cur.close()
        conn.close()
        return False, str(err)


# ---------------------------------------------
# Customer Queries
# ---------------------------------------------
def get_all_customers(search_term=""):
    conn = get_connection()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    query = """
        SELECT 
            b.mobile, 
            b.name, 
            b.address,
            COUNT(bl.BillNo) as total_bills,
            COALESCE(SUM(bl.total), 0) as total_spent,
            COALESCE(SUM(CASE WHEN bl.status = 'Pending' THEN bl.total ELSE 0 END), 0) as pending_dues
        FROM buyer b
        LEFT JOIN bill bl ON b.mobile = bl.mobile
    """
    if search_term:
        term = f"%{search_term}%"
        query += " WHERE b.name LIKE %s OR CAST(b.mobile AS CHAR) LIKE %s "
        query += " GROUP BY b.mobile, b.name, b.address ORDER BY b.name"
        cur.execute(query, (term, term))
    else:
        query += " GROUP BY b.mobile, b.name, b.address ORDER BY b.name"
        cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_customer(mobile):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT mobile, name, address FROM buyer WHERE mobile = %s", (mobile,))
    cust = cur.fetchone()
    cur.close()
    conn.close()
    return cust


def save_customer(mobile, name, address):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO buyer (mobile, name, address) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address)
        """, (mobile, name, address))
        conn.commit()
        cur.close()
        conn.close()
        return True, "Customer saved successfully"
    except Error as err:
        cur.close()
        conn.close()
        return False, str(err)


# ---------------------------------------------
# Billing & POS Queries
# ---------------------------------------------
def get_next_bill_no():
    conn = get_connection()
    if not conn:
        return 1001
    cur = conn.cursor()
    cur.execute("SELECT COALESCE(MAX(BillNo), 1000) + 1 FROM bill")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return int(val)


def process_checkout(bill_no, mobile, cust_name, cust_addr, mode, status, cart_items, total):
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    conn.autocommit = False
    cur = conn.cursor()
    try:
        # 1. Ensure customer is registered
        cur.execute("""
            INSERT INTO buyer (mobile, name, address) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address)
        """, (mobile, cust_name, cust_addr))

        # 2. Insert bill header
        cur.execute("""
            INSERT INTO bill (BillNo, mobile, `date`, mode, status, total) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (bill_no, mobile, date.today(), mode, status, total))

        # 3. Insert bill items and decrement stock
        for item in cart_items:
            cur.execute("""
                INSERT INTO bill_items (BillNo, PID, PName, price, quantity, item_total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bill_no, item['pid'], item['name'], item['price'], item['qty'], item['subtotal']))

            cur.execute("UPDATE products SET stock = stock - %s WHERE PID = %s", (item['qty'], item['pid']))

        conn.commit()
        cur.close()
        conn.close()
        return True, "Bill generated successfully"
    except Error as err:
        conn.rollback()
        cur.close()
        conn.close()
        return False, str(err)


def get_bill_details(bill_no):
    conn = get_connection()
    if not conn:
        return None
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT b.BillNo, b.mobile, b.date, b.mode, b.status, b.total, c.name, c.address 
        FROM bill b
        LEFT JOIN buyer c ON b.mobile = c.mobile
        WHERE b.BillNo = %s
    """, (bill_no,))
    header = cur.fetchone()
    if not header:
        cur.close()
        conn.close()
        return None

    cur.execute("""
        SELECT PID, PName, price, quantity, item_total 
        FROM bill_items 
        WHERE BillNo = %s
    """, (bill_no,))
    items = cur.fetchall()
    cur.close()
    conn.close()
    header['items'] = items
    return header


def settle_bill_due(bill_no):
    conn = get_connection()
    if not conn:
        return False
    cur = conn.cursor()
    try:
        cur.execute("UPDATE bill SET status = 'Paid' WHERE BillNo = %s", (bill_no,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Error:
        cur.close()
        conn.close()
        return False


# ---------------------------------------------
# Analytics & Reports Queries
# ---------------------------------------------
def get_analytics_metrics():
    conn = get_connection()
    if not conn:
        return {}
    cur = conn.cursor(dictionary=True)
    today = date.today()

    # Today's Revenue & Bills
    cur.execute("SELECT COUNT(*) as bills, COALESCE(SUM(total), 0) as rev FROM bill WHERE `date` = %s", (today,))
    today_res = cur.fetchone()

    # Lifetime Revenue & Bills
    cur.execute("SELECT COUNT(*) as bills, COALESCE(SUM(total), 0) as rev FROM bill")
    all_res = cur.fetchone()

    # Total Pending Dues
    cur.execute("SELECT COUNT(*) as count, COALESCE(SUM(total), 0) as due FROM bill WHERE status = 'Pending'")
    pending_res = cur.fetchone()

    # Low Stock Items count
    cur.execute("SELECT COUNT(*) as count FROM products WHERE stock <= 5")
    low_stock_res = cur.fetchone()

    # 7-Day Revenue Trend
    days = []
    revs = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        cur.execute("SELECT COALESCE(SUM(total), 0) FROM bill WHERE `date` = %s", (d,))
        r = cur.fetchone()['COALESCE(SUM(total), 0)']
        days.append(d.strftime("%b %d"))
        revs.append(float(r))

    # Top 5 Best Selling Products
    cur.execute("""
        SELECT PName, SUM(quantity) as sold, SUM(item_total) as revenue 
        FROM bill_items 
        GROUP BY PID, PName 
        ORDER BY sold DESC 
        LIMIT 5
    """)
    top_products = cur.fetchall()

    # Low stock list
    cur.execute("SELECT PID, PName, Price, stock FROM products WHERE stock <= 5 ORDER BY stock ASC")
    low_stock_items = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "today_revenue": float(today_res['rev']),
        "today_bills": int(today_res['bills']),
        "lifetime_revenue": float(all_res['rev']),
        "lifetime_bills": int(all_res['bills']),
        "pending_dues_total": float(pending_res['due']),
        "pending_dues_count": int(pending_res['count']),
        "low_stock_count": int(low_stock_res['count']),
        "trend_days": days,
        "trend_revs": revs,
        "top_products": top_products,
        "low_stock_items": low_stock_items
    }
