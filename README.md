# NAS Daily Needs - Store Billing, Inventory & Analytics System

A comprehensive Python and MySQL-based Retail Point of Sale (POS), Inventory Control, and Customer Management System designed for daily-needs and grocery stores.

---

## 🌟 Key Features & Improvisations

### 1. Inventory & Stock Management
- **Live Stock Tracking**: Each product tracks available stock quantity. Stock is automatically decremented upon billing.
- **Stock Warnings**: Automatic indicators for `Available`, `LOW STOCK! (<= 5 units)`, and `OUT OF STOCK (0)`.
- **Search Capabilities**: Find products instantly by name or PID using partial matching.
- **Product Editing & Restocking**: Easily change prices, add fresh stock shipments, or update product names without re-creating records.

### 2. Point of Sale (POS) & Billing
- **Quantity Support**: Add items to cart with custom quantities (e.g., 3x Milk, 2x Bread) without repeating product entry.
- **Stock Validation**: Prevents cashiers from selling more items than are physically in stock.
- **Auto-Generated Bill Numbers**: Automatically suggests the next sequential Bill Number (`MAX(BillNo) + 1`), preventing duplicate key errors while allowing manual override.
- **Itemized Bill History (`bill_items`)**: Every item, quantity, unit price, and subtotal is saved permanently, allowing full reprinting of any past invoice.
- **Multiple Payment Modes**: Supports `Cash`, `UPI`, `Card`, and `PayLater` with `Paid` or `Pending` statuses.

### 3. Customer Management & Purchase Tracking
- **Customer Directory**: Validates and stores 10-digit mobile numbers with customer names and addresses.
- **Purchase History**: View lifetime spend, total bill count, and individual past transactions for any customer.
- **Invoice Reprint**: View and reprint the complete receipt for any past bill.

### 4. Business Analytics & Reports
- **Daily Sales Dashboard**: Displays today's bill count and revenue.
- **Lifetime Revenue & Metrics**: Lifetime revenue and sales volume.
- **Pending Dues Tracker**: Lists all customers with unpaid / pending tabs.
- **Low Stock Alerts**: Identifies inventory needing restock.
- **Top 5 Best-Selling Products**: Highlights top-performing items by sales volume and revenue.

---

## 🗄️ Database Architecture

The system uses a normalized relational schema in MySQL:

```
[ products ]
  ├── PID (VARCHAR(10), Primary Key)
  ├── PName (VARCHAR(50))
  ├── Price (FLOAT)
  └── stock (INT)

[ buyer ]
  ├── mobile (BIGINT, Primary Key)
  ├── name (VARCHAR(100))
  └── address (VARCHAR(255))

[ bill ]
  ├── BillNo (INT, Primary Key)
  ├── mobile (BIGINT, Foreign Reference)
  ├── date (DATE)
  ├── mode (VARCHAR(30))
  ├── status (VARCHAR(30))
  └── total (FLOAT)

[ bill_items ]
  ├── id (INT, Primary Key, Auto Increment)
  ├── BillNo (INT, Indexed)
  ├── PID (VARCHAR(10))
  ├── PName (VARCHAR(50))
  ├── price (FLOAT)
  ├── quantity (INT)
  └── item_total (FLOAT)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Server 8.0+
- `mysql-connector-python`

Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration
Credentials can be configured via environment variables or use the default local configuration:
- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_USER` (default: `root`)
- `MYSQL_PASSWORD` (default: `saini`)
- `MYSQL_DATABASE` (default: `counter`)

### Running the App
```bash
python NASDailyneeds.py
```

---

## 📋 System Menu

```text
==================================================
             NAS DAILY NEEDS - MAIN MENU
==================================================
  [INVENTORY MANAGEMENT]
   1. View All Products (Stock & Prices)
   2. Search Product (by Name or PID)
   3. Add New Product
   4. Update Product (Price / Restock / Name)
   5. Remove Product

  [BILLING & POS]
   6. New Bill / Checkout
   7. View / Reprint Bill by Bill No

  [CUSTOMERS & ANALYTICS]
   8. Register / Update Customer
   9. Customer Details & Purchase History
  10. Business Analytics & Daily Sales Report

  [SYSTEM]
  11. Exit System
==================================================
```
