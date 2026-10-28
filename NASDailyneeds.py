import mysql.connector as n1
from datetime import date

# ==========================================
# MySQL Database Connection & Initialization
# ==========================================
try:
    # Connect to MySQL Server
    shop = n1.connect(host="localhost", user="root", passwd="saini")
    cur = shop.cursor()

    # Create and select database
    cur.execute("CREATE DATABASE IF NOT EXISTS counter")
    cur.execute("USE counter")

    # Create tables if they do not exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        PID VARCHAR(10) PRIMARY KEY,
        PName VARCHAR(50) NOT NULL,
        Price FLOAT NOT NULL
    )
    """)

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
    shop.commit()
    print("Connected to MySQL and database 'counter' successfully!")
except n1.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)


cart = []


def showitems():
    print("\n" + "=" * 45)
    print(f"{'PID':<10} {'Product Name':<22} {'Price (Rs)':<10}")
    print("-" * 45)
    cur.execute("SELECT PID, PName, Price FROM products")
    z = cur.fetchall()
    if not z:
        print("No products available.")
    else:
        for i in z:
            print(f"{str(i[0]):<10} {str(i[1]):<22} {float(i[2]):<10.2f}")
    print("=" * 45)


def newproduct():
    print("\n--- Add New Product ---")
    x = input("Enter Product ID: ").strip()
    if not x:
        print("Product ID cannot be empty!")
        return
    y = input("Enter Product Name: ").strip()
    try:
        z = float(input("Enter Price of the Product: "))
    except ValueError:
        print("Invalid Price! Please enter a valid number.")
        return

    sql = "INSERT INTO products (PID, PName, Price) VALUES (%s, %s, %s)"
    try:
        cur.execute(sql, (x, y, z))
        shop.commit()
        print(f"Product '{y}' (PID: {x}) added successfully!")
    except n1.IntegrityError:
        print(f"Error: Product with PID '{x}' already exists!")


def removeproduct():
    print("\n--- Remove Product ---")
    z = input("Enter the PID of Item to be Removed: ").strip()
    cur.execute("DELETE FROM products WHERE PID = %s", (z,))
    shop.commit()
    if cur.rowcount > 0:
        print(f"Item with PID '{z}' has been removed successfully.")
    else:
        print(f"Item with PID '{z}' not found.")


def newbuyer():
    print("\n--- Register New Customer ---")
    x = 0
    while True:
        try:
            x = int(input("Enter 10-Digit Mobile Number: "))
            if 1000000000 <= x <= 9999999999:
                break
            else:
                print("Invalid Number! Must be a 10-digit number.")
        except ValueError:
            print("Please enter digits only!")

    y = input("Enter Customer Name: ").strip()
    z = input("Enter Customer Address: ").strip()
    sql = "INSERT INTO buyer (mobile, name, address) VALUES (%s, %s, %s)"
    try:
        cur.execute(sql, (x, y, z))
        shop.commit()
        print(f"Customer '{y}' registered successfully!")
    except n1.IntegrityError:
        print(f"Customer with mobile {x} already exists. Updating details...")
        cur.execute("UPDATE buyer SET name = %s, address = %s WHERE mobile = %s", (y, z, x))
        shop.commit()
        print("Customer details updated successfully!")


def bag():
    global cart
    cart = []
    cur.execute("SELECT PID, PName, Price FROM products")
    z = cur.fetchall()
    if not z:
        print("No products available to purchase!")
        return

    valid_pids = [str(item[0]) for item in z]
    print("\nAvailable Products:")
    print("-" * 45)
    print(f"{'PID':<10} {'Product Name':<22} {'Price (Rs)':<10}")
    print("-" * 45)
    for item in z:
        print(f"{str(item[0]):<10} {str(item[1]):<22} {float(item[2]):<10.2f}")
    print("-" * 45)

    while True:
        a = input("Enter PID to add to cart (or 0 to finish): ").strip()
        if a == '0':
            break
        if a in valid_pids:
            cart.append(a)
            print(f"-> Added PID '{a}' to cart. Total items in cart: {len(cart)}")
        else:
            print(f"Invalid PID '{a}'! Please enter a valid PID from the list or '0' to finish.")


def bill():
    global cart
    if not cart:
        print("Cart is empty! No bill created.")
        return

    print("\n--- Billing ---")
    try:
        new = int(input("Is this an Old Customer? (1. Yes / 2. No): "))
    except ValueError:
        new = 2

    if new != 1:
        newbuyer()

    dated = date.today()
    while True:
        try:
            x = int(input("Enter Bill No.: "))
            cur.execute("SELECT BillNo FROM bill WHERE BillNo = %s", (x,))
            if cur.fetchone():
                print(f"Bill No. {x} already exists! Please use a different Bill No.")
                continue
            break
        except ValueError:
            print("Please enter a valid numeric Bill Number!")

    y = 0
    while True:
        try:
            y = int(input("Enter 10-Digit Customer Mobile: "))
            if 1000000000 <= y <= 9999999999:
                break
            else:
                print("Invalid Number! Must be a 10-digit number.")
        except ValueError:
            print("Please enter digits only!")

    # Check if buyer exists; if not, add record
    cur.execute("SELECT name FROM buyer WHERE mobile = %s", (y,))
    buyer_record = cur.fetchone()
    if not buyer_record:
        print("Customer not registered in records. Adding quick details...")
        b_name = input("Enter Customer Name: ").strip() or "Customer"
        b_addr = input("Enter Customer Address: ").strip() or "N/A"
        cur.execute("INSERT INTO buyer (mobile, name, address) VALUES (%s, %s, %s)", (y, b_name, b_addr))
        shop.commit()

    mode = input("Payment Mode (Cash, Card, UPI, PayLater): ").strip()
    status = ""
    while status not in ["Paid", "Pending"]:
        try:
            z = int(input("(1) Paid / (2) Pending: "))
            if z == 1:
                status = "Paid"
            elif z == 2:
                status = "Pending"
            else:
                print("Choose 1 for Paid or 2 for Pending.")
        except ValueError:
            print("Please enter 1 or 2.")

    # Calculate total safely using parameterized queries
    total = 0.0
    for i in cart:
        cur.execute("SELECT Price FROM products WHERE PID = %s", (i,))
        k = cur.fetchone()
        if k:
            total += float(k[0])

    sql = "INSERT INTO bill (BillNo, mobile, `date`, mode, status, total) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (x, y, dated, mode, status, total)
    cur.execute(sql, val)
    shop.commit()

    # Print Receipt
    print("\n" + "=" * 50)
    print(f"{'*** NAS DAILY NEEDS RECEIPT ***':^50}")
    print("=" * 50)
    print(f"Bill No: {x:<15} Date: {str(dated)}")
    print(f"Customer Mobile: {y}")
    print(f"Payment Mode: {mode:<12} Status: {status}")
    print("-" * 50)
    print(f"{'No.':<4} {'PID':<8} {'Product Name':<24} {'Price (Rs)':<10}")
    print("-" * 50)
    count = 0
    for i in cart:
        count += 1
        cur.execute("SELECT PID, PName, Price FROM products WHERE PID = %s", (i,))
        val = cur.fetchone()
        if val:
            print(f"{count:<4} {str(val[0]):<8} {str(val[1]):<24} {float(val[2]):<10.2f}")
    print("-" * 50)
    print(f"{'Total Amount:':<38} Rs. {total:.2f}")
    print("=" * 50)
    print(f"{'Thank you for shopping with us!':^50}\n")
    cart = []


def buyer():
    print("\n--- Search Customer Details ---")
    val = 0
    while True:
        try:
            val = int(input("Enter 10-Digit Mobile Number: "))
            if 1000000000 <= val <= 9999999999:
                break
            else:
                print("Invalid Number! Must be a 10-digit number.")
        except ValueError:
            print("Please enter digits only!")

    cur.execute("SELECT mobile, name, address FROM buyer WHERE mobile = %s", (val,))
    buyer_info = cur.fetchone()
    if not buyer_info:
        print(f"No customer found with mobile number: {val}")
        return

    print("\n" + "=" * 55)
    print(f"Customer Name   : {buyer_info[1]}")
    print(f"Mobile Number   : {buyer_info[0]}")
    print(f"Address         : {buyer_info[2]}")
    print("-" * 55)

    cur.execute("SELECT BillNo, `date`, mode, status, total FROM bill WHERE mobile = %s", (val,))
    bills = cur.fetchall()
    if bills:
        print("Billing History:")
        print(f"{'Bill No':<10} {'Date':<15} {'Mode':<12} {'Status':<10} {'Total (Rs)':<10}")
        print("-" * 55)
        for b in bills:
            print(f"{b[0]:<10} {str(b[1]):<15} {b[2]:<12} {b[3]:<10} {float(b[4]):<10.2f}")
    else:
        print("No billing history found for this customer.")
    print("=" * 55)


def page():
    while True:
        print("\n" + "=" * 35)
        print("             MENU")
        print("=" * 35)
        print("1. Add New Product")
        print("2. View Available Products")
        print("3. Remove Existing Product")
        print("4. Billing")
        print("5. New Customer")
        print("6. Customer Details")
        print("7. Exit")
        print("=" * 35)
        try:
            choice = int(input("Enter Your Choice (1-7): "))
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 7.")
            continue

        if choice == 1:
            newproduct()
        elif choice == 2:
            showitems()
        elif choice == 3:
            print("\nExisting Products:")
            showitems()
            removeproduct()
        elif choice == 4:
            bag()
            if cart:
                bill()
        elif choice == 5:
            newbuyer()
        elif choice == 6:
            buyer()
        elif choice == 7:
            print("Exiting Menu...")
            break
        else:
            print("Invalid Choice! Please enter a number between 1 and 7.")


def start():
    print("\n" + "*" * 49)
    print("*********       NAS DAILY NEEDS         *********")
    print("*" * 49)
    print("1. Enter System")
    print("2. Exit")
    print("*" * 49)


if __name__ == "__main__":
    start()
    while True:
        try:
            ch = int(input("Enter Number to Continue (1-2): "))
            if ch == 1:
                page()
                start()
            elif ch == 2:
                print("Thank You for using NAS DAILY NEEDS System! Goodbye!")
                break
            else:
                print("Invalid Choice! Try Again.")
                start()
        except ValueError:
            print("Invalid Input! Please enter 1 or 2.")
            start()
        except KeyboardInterrupt:
            print("\nOperation cancelled. Exiting...")
            break
