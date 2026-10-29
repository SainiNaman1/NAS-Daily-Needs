import os
import sys
from datetime import date
import mysql.connector as n1
from mysql.connector import Error

# ==========================================
# Database Connection & Migration Helper
# ==========================================
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASSWORD", "saini")
DB_NAME = os.getenv("MYSQL_DATABASE", "counter")

try:
    # 1. Connect to MySQL Server
    shop = n1.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS)
    cur = shop.cursor()

    # 2. Ensure database exists
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
    cur.execute(f"USE `{DB_NAME}`")

    # 3. Ensure tables exist with modern schema
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        PID VARCHAR(10) PRIMARY KEY,
        PName VARCHAR(50) NOT NULL,
        Price FLOAT NOT NULL,
        stock INT NOT NULL DEFAULT 50
    )
    """)

    # Check and add stock column if missing from older schema
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

    shop.commit()
    print("Database connection and schema verified successfully!")
except Error as err:
    print(f"Error connecting to MySQL: {err}")
    print("Please check your MySQL service and credentials.")
    sys.exit(1)


# Global cart structure:
# Each item: {'pid': str, 'name': str, 'price': float, 'qty': int, 'subtotal': float}
cart = []


# ==========================================
# 1. Inventory & Product Management
# ==========================================
def showitems():
    print("\n" + "=" * 68)
    print(f"{'PID':<8} {'Product Name':<28} {'Price (Rs)':<12} {'Stock':<8} {'Status':<10}")
    print("-" * 68)
    cur.execute("SELECT PID, PName, Price, stock FROM products ORDER BY PID")
    items = cur.fetchall()
    if not items:
        print("No products available in the inventory.")
    else:
        for p in items:
            pid, name, price, stock = p[0], p[1], float(p[2]), int(p[3])
            if stock == 0:
                status = "OUT OF STOCK"
            elif stock <= 5:
                status = "LOW STOCK!"
            else:
                status = "Available"
            print(f"{str(pid):<8} {name:<28} {price:<12.2f} {stock:<8} {status:<10}")
    print("=" * 68)


def searchproduct():
    print("\n--- Search Products ---")
    term = input("Enter Product ID or Name to search: ").strip()
    if not term:
        print("Search term cannot be empty.")
        return

    cur.execute("""
        SELECT PID, PName, Price, stock FROM products 
        WHERE PID LIKE %s OR PName LIKE %s 
        ORDER BY PName
    """, (f"%{term}%", f"%{term}%"))
    results = cur.fetchall()

    if not results:
        print(f"No products found matching '{term}'.")
        return

    print("\n" + "=" * 68)
    print(f"{'PID':<8} {'Product Name':<28} {'Price (Rs)':<12} {'Stock':<8} {'Status':<10}")
    print("-" * 68)
    for p in results:
        pid, name, price, stock = p[0], p[1], float(p[2]), int(p[3])
        status = "OUT OF STOCK" if stock == 0 else ("LOW STOCK!" if stock <= 5 else "Available")
        print(f"{str(pid):<8} {name:<28} {price:<12.2f} {stock:<8} {status:<10}")
    print("=" * 68)


def newproduct():
    print("\n--- Add New Product ---")
    pid = input("Enter Product ID (PID): ").strip()
    if not pid:
        print("Product ID cannot be empty!")
        return

    cur.execute("SELECT PName FROM products WHERE PID = %s", (pid,))
    if cur.fetchone():
        print(f"Error: Product with PID '{pid}' already exists! Use 'Update Product' to modify it.")
        return

    name = input("Enter Product Name: ").strip()
    if not name:
        print("Product Name cannot be empty!")
        return

    while True:
        try:
            price = float(input("Enter Price of the Product (Rs): "))
            if price < 0:
                print("Price cannot be negative!")
                continue
            break
        except ValueError:
            print("Invalid price! Please enter a numeric value.")

    while True:
        try:
            stock = int(input("Enter Initial Stock Quantity (default 50): ") or "50")
            if stock < 0:
                print("Stock cannot be negative!")
                continue
            break
        except ValueError:
            print("Invalid stock! Please enter an integer.")

    sql = "INSERT INTO products (PID, PName, Price, stock) VALUES (%s, %s, %s, %s)"
    try:
        cur.execute(sql, (pid, name, price, stock))
        shop.commit()
        print(f"Product '{name}' (PID: {pid}, Stock: {stock}) added successfully!")
    except Error as err:
        print(f"Database error: {err}")


def updateproduct():
    print("\n--- Update Existing Product ---")
    pid = input("Enter PID of product to update: ").strip()
    cur.execute("SELECT PID, PName, Price, stock FROM products WHERE PID = %s", (pid,))
    item = cur.fetchone()
    if not item:
        print(f"Product with PID '{pid}' does not exist.")
        return

    print(f"\nCurrent Details: Name='{item[1]}', Price=Rs.{item[2]:.2f}, Stock={item[3]}")
    print("What would you like to update?")
    print("1. Update Price")
    print("2. Restock (Add Quantity)")
    print("3. Set Exact Stock")
    print("4. Update Name")
    print("5. Cancel")

    try:
        choice = int(input("Choose an option (1-5): "))
    except ValueError:
        print("Invalid choice.")
        return

    if choice == 1:
        try:
            new_price = float(input("Enter new price (Rs): "))
            if new_price < 0:
                print("Price cannot be negative!")
                return
            cur.execute("UPDATE products SET Price = %s WHERE PID = %s", (new_price, pid))
            shop.commit()
            print(f"Price updated to Rs. {new_price:.2f}")
        except ValueError:
            print("Invalid price entered.")
    elif choice == 2:
        try:
            add_qty = int(input("Enter quantity to ADD to current stock: "))
            if add_qty <= 0:
                print("Quantity must be positive!")
                return
            cur.execute("UPDATE products SET stock = stock + %s WHERE PID = %s", (add_qty, pid))
            shop.commit()
            print(f"Added {add_qty} units. New stock: {item[3] + add_qty}")
        except ValueError:
            print("Invalid quantity entered.")
    elif choice == 3:
        try:
            new_stock = int(input("Enter new total stock quantity: "))
            if new_stock < 0:
                print("Stock cannot be negative!")
                return
            cur.execute("UPDATE products SET stock = %s WHERE PID = %s", (new_stock, pid))
            shop.commit()
            print(f"Stock set to {new_stock} units.")
        except ValueError:
            print("Invalid stock entered.")
    elif choice == 4:
        new_name = input("Enter new product name: ").strip()
        if new_name:
            cur.execute("UPDATE products SET PName = %s WHERE PID = %s", (new_name, pid))
            shop.commit()
            print(f"Product name updated to '{new_name}'.")
        else:
            print("Name cannot be empty.")
    elif choice == 5:
        print("Update cancelled.")
    else:
        print("Invalid option.")


def removeproduct():
    print("\n--- Remove Product ---")
    pid = input("Enter the PID of Item to be Removed: ").strip()
    cur.execute("SELECT PName FROM products WHERE PID = %s", (pid,))
    item = cur.fetchone()
    if not item:
        print(f"Item with PID '{pid}' not found.")
        return

    confirm = input(f"Are you sure you want to delete '{item[0]}' (PID: {pid})? (y/n): ").strip().lower()
    if confirm == 'y':
        cur.execute("DELETE FROM products WHERE PID = %s", (pid,))
        shop.commit()
        print(f"Product '{item[0]}' (PID: {pid}) has been permanently removed.")
    else:
        print("Deletion cancelled.")


# ==========================================
# 2. Billing & Point of Sale (POS)
# ==========================================
def get_next_bill_no():
    cur.execute("SELECT COALESCE(MAX(BillNo), 1000) + 1 FROM bill")
    return int(cur.fetchone()[0])


def bag():
    global cart
    cart = []
    print("\n--- Add Items to Cart ---")
    showitems()

    while True:
        pid = input("\nEnter PID to add (or '0' when finished, 'C' to clear): ").strip()
        if pid == '0':
            break
        elif pid.upper() == 'C':
            cart = []
            print("Cart has been cleared.")
            continue

        cur.execute("SELECT PID, PName, Price, stock FROM products WHERE PID = %s", (pid,))
        item = cur.fetchone()
        if not item:
            print(f"Invalid PID '{pid}'! Please choose from available products.")
            continue

        p_id, p_name, p_price, p_stock = item[0], item[1], float(item[2]), int(item[3])

        # Check existing quantity in cart
        already_in_cart = sum(c['qty'] for c in cart if c['pid'] == p_id)
        available = p_stock - already_in_cart

        if available <= 0:
            print(f"Sorry, '{p_name}' is currently OUT OF STOCK (or all available stock is in your cart)!")
            continue

        try:
            qty_input = input(f"Enter Quantity for '{p_name}' (Available: {available}, default 1): ").strip()
            qty = int(qty_input) if qty_input else 1
            if qty <= 0:
                print("Quantity must be at least 1.")
                continue
            if qty > available:
                print(f"Cannot add {qty} units! Only {available} available in stock.")
                continue
        except ValueError:
            print("Invalid quantity! Please enter an integer.")
            continue

        # Add or update in cart
        existing = next((c for c in cart if c['pid'] == p_id), None)
        if existing:
            existing['qty'] += qty
            existing['subtotal'] = existing['qty'] * existing['price']
        else:
            cart.append({
                'pid': p_id,
                'name': p_name,
                'price': p_price,
                'qty': qty,
                'subtotal': p_price * qty
            })

        print(f"-> Added {qty}x '{p_name}' to cart.")
        
        # Display current cart total
        current_total = sum(c['subtotal'] for c in cart)
        print(f"Current Cart Items: {len(cart)} | Total: Rs. {current_total:.2f}")


def bill():
    global cart
    if not cart:
        print("Your cart is empty! Add products before billing.")
        return

    print("\n--- Checkout & Billing ---")
    auto_bill_no = get_next_bill_no()
    
    # Bill Number Selection
    while True:
        b_input = input(f"Enter Bill No. [Press Enter for Auto: {auto_bill_no}]: ").strip()
        if not b_input:
            bill_no = auto_bill_no
            break
        try:
            bill_no = int(b_input)
            cur.execute("SELECT BillNo FROM bill WHERE BillNo = %s", (bill_no,))
            if cur.fetchone():
                print(f"Bill No. {bill_no} already exists! Please choose another.")
                continue
            break
        except ValueError:
            print("Bill No. must be a valid number.")

    # Customer Mobile
    mobile = 0
    while True:
        try:
            m_input = input("Enter 10-Digit Customer Mobile: ").strip()
            mobile = int(m_input)
            if 1000000000 <= mobile <= 9999999999:
                break
            else:
                print("Invalid Mobile Number! Must be 10 digits.")
        except ValueError:
            print("Please enter numeric digits only!")

    # Check Customer Registration
    cur.execute("SELECT name, address FROM buyer WHERE mobile = %s", (mobile,))
    buyer_record = cur.fetchone()
    if buyer_record:
        cust_name = buyer_record[0]
        cust_addr = buyer_record[1]
        print(f"Found Registered Customer: {cust_name} ({cust_addr})")
    else:
        print(f"Customer with mobile {mobile} is not registered.")
        cust_name = input("Enter Customer Name: ").strip() or "Walk-in Customer"
        cust_addr = input("Enter Customer Address: ").strip() or "Local"
        cur.execute("INSERT INTO buyer (mobile, name, address) VALUES (%s, %s, %s)", 
                    (mobile, cust_name, cust_addr))
        shop.commit()
        print("Customer registered successfully.")

    # Payment Mode
    print("\nPayment Modes: (1) Cash  (2) UPI  (3) Card  (4) PayLater")
    mode_map = {"1": "Cash", "2": "UPI", "3": "Card", "4": "PayLater"}
    while True:
        m_choice = input("Select Payment Mode (1-4, default Cash): ").strip() or "1"
        if m_choice in mode_map:
            mode = mode_map[m_choice]
            break
        print("Invalid selection. Choose 1, 2, 3, or 4.")

    # Payment Status
    status_map = {"1": "Paid", "2": "Pending"}
    default_status = "Pending" if mode == "PayLater" else "Paid"
    default_code = "2" if default_status == "Pending" else "1"
    while True:
        s_choice = input(f"Payment Status (1. Paid / 2. Pending) [default {default_status}]: ").strip() or default_code
        if s_choice in status_map:
            status = status_map[s_choice]
            break
        print("Please choose 1 for Paid or 2 for Pending.")

    # Total Calculation
    total_amount = sum(c['subtotal'] for c in cart)
    bill_date = date.today()

    # Database Transaction
    try:
        # 1. Insert header bill
        cur.execute("""
            INSERT INTO bill (BillNo, mobile, `date`, mode, status, total) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (bill_no, mobile, bill_date, mode, status, total_amount))

        # 2. Insert line items & deduct stock
        for item in cart:
            cur.execute("""
                INSERT INTO bill_items (BillNo, PID, PName, price, quantity, item_total)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (bill_no, item['pid'], item['name'], item['price'], item['qty'], item['subtotal']))

            cur.execute("""
                UPDATE products SET stock = stock - %s WHERE PID = %s
            """, (item['qty'], item['pid']))

        shop.commit()
    except Error as err:
        shop.rollback()
        print(f"Transaction failed! Error: {err}")
        return

    # Print Formatted Receipt
    print("\n" + "=" * 60)
    print(f"{'*** NAS DAILY NEEDS RECEIPT ***':^60}")
    print("=" * 60)
    print(f"Bill No  : {bill_no:<20} Date  : {str(bill_date)}")
    print(f"Customer : {cust_name:<20} Mobile: {mobile}")
    print(f"Mode     : {mode:<20} Status: {status}")
    print("-" * 60)
    print(f"{'No.':<4} {'PID':<7} {'Item Name':<22} {'Price':<9} {'Qty':<5} {'Total (Rs)':<10}")
    print("-" * 60)
    for idx, item in enumerate(cart, 1):
        print(f"{idx:<4} {item['pid']:<7} {item['name']:<22} {item['price']:<9.2f} {item['qty']:<5} {item['subtotal']:<10.2f}")
    print("-" * 60)
    print(f"{'GRAND TOTAL:':<48} Rs. {total_amount:.2f}")
    print("=" * 60)
    print(f"{'Thank you for shopping with us!':^60}\n")

    cart = []


def viewbill():
    print("\n--- View / Reprint Bill ---")
    try:
        bill_no = int(input("Enter Bill Number: "))
    except ValueError:
        print("Invalid Bill Number.")
        return

    cur.execute("""
        SELECT b.BillNo, b.mobile, b.date, b.mode, b.status, b.total, c.name, c.address 
        FROM bill b
        LEFT JOIN buyer c ON b.mobile = c.mobile
        WHERE b.BillNo = %s
    """, (bill_no,))
    bill_data = cur.fetchone()

    if not bill_data:
        print(f"Bill No. {bill_no} not found.")
        return

    b_no, mobile, b_date, mode, status, total, c_name, c_addr = bill_data
    c_name = c_name or "Unknown Customer"

    cur.execute("SELECT PID, PName, price, quantity, item_total FROM bill_items WHERE BillNo = %s", (bill_no,))
    items = cur.fetchall()

    print("\n" + "=" * 60)
    print(f"{'*** NAS DAILY NEEDS INVOICE ***':^60}")
    print("=" * 60)
    print(f"Bill No  : {b_no:<20} Date  : {str(b_date)}")
    print(f"Customer : {c_name:<20} Mobile: {mobile}")
    print(f"Address  : {c_addr or 'N/A'}")
    print(f"Mode     : {mode:<20} Status: {status}")
    print("-" * 60)
    print(f"{'No.':<4} {'PID':<7} {'Item Name':<22} {'Price':<9} {'Qty':<5} {'Total (Rs)':<10}")
    print("-" * 60)

    if items:
        for idx, it in enumerate(items, 1):
            print(f"{idx:<4} {it[0]:<7} {it[1]:<22} {float(it[2]):<9.2f} {it[3]:<5} {float(it[4]):<10.2f}")
    else:
        print("  (Detailed line items not available for legacy records)")

    print("-" * 60)
    print(f"{'GRAND TOTAL:':<48} Rs. {float(total):.2f}")
    print("=" * 60)


# ==========================================
# 3. Customer Management
# ==========================================
def newbuyer():
    print("\n--- Register / Update Customer ---")
    while True:
        try:
            mobile = int(input("Enter 10-Digit Mobile Number: "))
            if 1000000000 <= mobile <= 9999999999:
                break
            print("Invalid Number! Must be 10 digits.")
        except ValueError:
            print("Please enter digits only!")

    name = input("Enter Customer Name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    address = input("Enter Customer Address: ").strip()

    sql = """
        INSERT INTO buyer (mobile, name, address) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), address = VALUES(address)
    """
    cur.execute(sql, (mobile, name, address))
    shop.commit()
    print(f"Customer '{name}' (Mobile: {mobile}) saved successfully!")


def buyer():
    print("\n--- Search Customer Purchase History ---")
    while True:
        try:
            mobile = int(input("Enter 10-Digit Mobile Number: "))
            if 1000000000 <= mobile <= 9999999999:
                break
            print("Invalid Number! Must be 10 digits.")
        except ValueError:
            print("Please enter digits only!")

    cur.execute("SELECT mobile, name, address FROM buyer WHERE mobile = %s", (mobile,))
    cust = cur.fetchone()
    if not cust:
        print(f"No customer found with mobile {mobile}.")
        return

    print("\n" + "=" * 60)
    print(f"Customer Profile")
    print("-" * 60)
    print(f"Name    : {cust[1]}")
    print(f"Mobile  : {cust[0]}")
    print(f"Address : {cust[2]}")
    print("-" * 60)

    cur.execute("SELECT BillNo, `date`, mode, status, total FROM bill WHERE mobile = %s ORDER BY `date` DESC", (mobile,))
    bills = cur.fetchall()

    if bills:
        print(f"{'Bill No':<10} {'Date':<15} {'Mode':<12} {'Status':<10} {'Total (Rs)':<10}")
        print("-" * 60)
        total_spent = 0.0
        for b in bills:
            total_spent += float(b[4])
            print(f"{b[0]:<10} {str(b[1]):<15} {b[2]:<12} {b[3]:<10} {float(b[4]):<10.2f}")
        print("-" * 60)
        print(f"Lifetime Purchases: {len(bills)} Bills | Total Spent: Rs. {total_spent:.2f}")
        print("=" * 60)

        # Quick bill reprint option
        opt = input("\nEnter Bill No to view full receipt (or press Enter to return): ").strip()
        if opt:
            try:
                bno = int(opt)
                if any(b[0] == bno for b in bills):
                    # Call viewbill logic for this bno
                    cur.execute("""
                        SELECT b.BillNo, b.date, b.mode, b.status, b.total 
                        FROM bill b WHERE b.BillNo = %s
                    """, (bno,))
                    b_head = cur.fetchone()
                    cur.execute("SELECT PID, PName, price, quantity, item_total FROM bill_items WHERE BillNo = %s", (bno,))
                    b_items = cur.fetchall()
                    if b_head:
                        print("\n" + "=" * 55)
                        print(f"Bill #{b_head[0]} | Date: {b_head[1]} | Mode: {b_head[2]} | Status: {b_head[3]}")
                        print("-" * 55)
                        for it in b_items:
                            print(f"- {it[1]} ({it[0]}): {it[3]} x Rs.{it[2]:.2f} = Rs.{it[4]:.2f}")
                        print(f"Total: Rs. {b_head[4]:.2f}")
                        print("=" * 55)
            except ValueError:
                pass
    else:
        print("No purchase history found for this customer.")
        print("=" * 60)


# ==========================================
# 4. Analytics & Daily Reports
# ==========================================
def reports():
    today = date.today()
    print("\n" + "=" * 65)
    print(f"{'*** NAS DAILY NEEDS - BUSINESS ANALYTICS ***':^65}")
    print("=" * 65)

    # 1. Today's Summary
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bill WHERE `date` = %s", (today,))
    t_count, t_rev = cur.fetchone()
    print(f"[DATE] Today's Date           : {str(today)}")
    print(f"[BILLS] Today's Bills Generated: {t_count}")
    print(f"[REVENUE] Today's Revenue        : Rs. {float(t_rev):.2f}")
    print("-" * 65)

    # 2. Overall Lifetime Metrics
    cur.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM bill")
    all_count, all_rev = cur.fetchone()
    print(f"[LIFETIME] Total Lifetime Bills   : {all_count}")
    print(f"[REVENUE] Total Lifetime Revenue : Rs. {float(all_rev):.2f}")
    print("-" * 65)

    # 3. Pending Payments
    cur.execute("""
        SELECT b.BillNo, b.mobile, c.name, b.total, b.date 
        FROM bill b
        LEFT JOIN buyer c ON b.mobile = c.mobile
        WHERE b.status = 'Pending'
        ORDER BY b.date
    """)
    pending = cur.fetchall()
    pending_total = sum(float(p[3]) for p in pending)
    print(f"[PENDING]  Pending Dues Count     : {len(pending)} Bills (Total: Rs. {pending_total:.2f})")
    if pending:
        print(f"   {'BillNo':<8} {'Customer':<18} {'Mobile':<12} {'Due (Rs)':<10} {'Date':<12}")
        print("   " + "-" * 60)
        for p in pending[:5]:
            c_name = p[2] or "Unknown"
            print(f"   {p[0]:<8} {c_name:<18} {p[1]:<12} {float(p[3]):<10.2f} {str(p[4]):<12}")
        if len(pending) > 5:
            print(f"   ... and {len(pending) - 5} more pending bills.")
    print("-" * 65)

    # 4. Low Stock Alerts
    cur.execute("SELECT PID, PName, Price, stock FROM products WHERE stock <= 5 ORDER BY stock ASC")
    low_stock = cur.fetchall()
    print(f"[LOW STOCK] Low Stock Alerts (<= 5 units): {len(low_stock)} items")
    if low_stock:
        for ls in low_stock:
            st = f"OUT OF STOCK (0)" if ls[3] == 0 else f"{ls[3]} left"
            print(f"   - [{ls[0]}] {ls[1]}: {st}")
    else:
        print("   All products have healthy stock levels!")
    print("-" * 65)

    # 5. Top 5 Selling Products
    cur.execute("""
        SELECT PID, PName, SUM(quantity) as total_sold, SUM(item_total) as revenue 
        FROM bill_items 
        GROUP BY PID, PName 
        ORDER BY total_sold DESC 
        LIMIT 5
    """)
    top_sellers = cur.fetchall()
    print("[TOP SELLERS] Top 5 Best-Selling Products:")
    if top_sellers:
        print(f"   {'Rank':<6} {'PID':<8} {'Product Name':<22} {'Sold':<8} {'Revenue (Rs)':<12}")
        print("   " + "-" * 56)
        for idx, ts in enumerate(top_sellers, 1):
            print(f"   #{idx:<5} {ts[0]:<8} {ts[1]:<22} {ts[2]:<8} {float(ts[3]):<12.2f}")
    else:
        print("   No itemized sales data available yet.")
    print("=" * 65)


# ==========================================
# 5. Main Menus & Navigation
# ==========================================
def page():
    while True:
        print("\n" + "=" * 52)
        print("             NAS DAILY NEEDS - MAIN MENU")
        print("=" * 52)
        print("  [INVENTORY MANAGEMENT]")
        print("   1. View All Products (Stock & Prices)")
        print("   2. Search Product (by Name or PID)")
        print("   3. Add New Product")
        print("   4. Update Product (Price / Restock / Name)")
        print("   5. Remove Product")
        print("\n  [BILLING & POS]")
        print("   6. New Bill / Checkout")
        print("   7. View / Reprint Bill by Bill No")
        print("\n  [CUSTOMERS & ANALYTICS]")
        print("   8. Register / Update Customer")
        print("   9. Customer Details & Purchase History")
        print("  10. Business Analytics & Daily Sales Report")
        print("\n  [SYSTEM]")
        print("  11. Exit System")
        print("=" * 52)

        try:
            choice = int(input("Enter Your Choice (1-11): "))
        except ValueError:
            print("Invalid input! Please enter a number between 1 and 11.")
            continue

        if choice == 1:
            showitems()
        elif choice == 2:
            searchproduct()
        elif choice == 3:
            newproduct()
        elif choice == 4:
            updateproduct()
        elif choice == 5:
            removeproduct()
        elif choice == 6:
            bag()
            if cart:
                bill()
        elif choice == 7:
            viewbill()
        elif choice == 8:
            newbuyer()
        elif choice == 9:
            buyer()
        elif choice == 10:
            reports()
        elif choice == 11:
            print("Exiting system. Have a great day!")
            break
        else:
            print("Invalid choice! Please select an option between 1 and 11.")


def start():
    print("\n" + "*" * 52)
    print("*********       NAS DAILY NEEDS STORE       *********")
    print("*********    Inventory & Billing System     *********")
    print("*" * 52)
    print("1. Enter System")
    print("2. Exit")
    print("*" * 52)


if __name__ == "__main__":
    start()
    while True:
        try:
            ch = int(input("Enter Number to Continue (1-2): "))
            if ch == 1:
                page()
                start()
            elif ch == 2:
                print("Thank you for using NAS Daily Needs System! Goodbye!")
                break
            else:
                print("Invalid Choice! Please enter 1 or 2.")
                start()
        except ValueError:
            print("Invalid Input! Please enter 1 or 2.")
            start()
        except KeyboardInterrupt:
            print("\nOperation cancelled. Exiting...")
            break
