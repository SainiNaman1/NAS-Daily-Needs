# NAS Daily Needs - Store Billing & Inventory Management System

A Python and MySQL-based inventory, customer management, and retail billing system designed for grocery and daily-needs stores.

## Features

- **Product Management**: View product list, add new items with custom product IDs, and remove items.
- **Customer Registration**: Maintain customer database with 10-digit mobile numbers, names, and delivery addresses.
- **Dynamic Cart & Billing**:
  - Add items to cart interactively using Product IDs (PID).
  - Calculate totals dynamically using floating-point prices.
  - Record payment mode (`Cash`, `Card`, `UPI`, `PayLater`) and status (`Paid`, `Pending`).
  - Generate a formatted store receipt on checkout.
- **Customer Purchase History**: Look up any customer by phone number to see their profile and all past transaction bills.
- **Auto-Initialization**: Automatically creates the database `counter` and all necessary tables (`products`, `buyer`, `bill`) on first run if they don't already exist.

---

## Prerequisites

1. **Python 3.x**
2. **MySQL Server** running locally (or remote)
3. Python MySQL connector library:
   ```bash
   pip install -r requirements.txt
   ```

---

## Database Configuration

By default, the script connects to `localhost` with user `root`. Adjust credentials in `NASDailyneeds.py` if your MySQL password differs:

```python
shop = n1.connect(host="localhost", user="root", passwd="YOUR_PASSWORD")
```

To manually initialize the database with sample products and customers, you can also run:
```bash
mysql -u root -p < schema.sql
```

---

## How to Run

Run the main application script:

```bash
python NASDailyneeds.py
```

### Main Menu Options

```text
===================================
             MENU
===================================
1. Add New Product
2. View Available Products
3. Remove Existing Product
4. Billing
5. New Customer
6. Customer Details
7. Exit
===================================
```

---

## Project Structure

```text
NAS-Daily-Needs/
├── NASDailyneeds.py   # Main Python CLI application
├── schema.sql         # SQL schema definition and sample data
├── requirements.txt   # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # Project documentation
```
