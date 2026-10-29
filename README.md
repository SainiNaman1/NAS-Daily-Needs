# NAS Daily Needs - Enterprise POS & Retail ERP

A high-performance, enterprise-grade Desktop Point of Sale (POS), Inventory Control, Customer CRM & Khata Ledger, and Business Analytics system designed for retail and grocery stores.

Built with **PyQt6**, **MySQL 8.0**, **Matplotlib**, and dynamic **UPI QR Codes**.

---

## 🚀 Key Modules & Capabilities

### 🛒 1. Interactive Point of Sale (POS) Terminal (`F1`)
- **Live Search & Auto-Filter**: Search products instantly by Name or Product ID (PID).
- **Interactive Cart**: Real-time quantity controls (`-` / `+`), item subtotal calculation, and stock validation limits.
- **Smart Customer Lookup**: Automatically detects registered customers when a 10-digit phone number is entered.
- **Dynamic UPI QR Code**: Generates real UPI payment QR codes (`upi://pay?pa=...`) for instant mobile scan-and-pay.
- **Printable Invoices**: Generates thermal receipts with store GSTIN details, one-click print dialog, and Save as PDF.

### 📦 2. Inventory & Stock Management (`F2`)
- **Live Inventory Health**: Color-coded badges for `In Stock`, `LOW STOCK (<=5 units)`, and `OUT OF STOCK`.
- **Full CRUD Support**: Add new items, restock shipments, edit prices, or delete discontinued products.
- **Inventory Valuation**: Calculates total retail stock value automatically.

### 👥 3. Customer CRM & Khata Ledger (`F3`)
- **Customer Directory**: Track customer lifetime spend, bill count, and outstanding tabs.
- **Purchase History**: Complete log of all past transactions.
- **Khata Settlement**: Mark unpaid `PayLater` / Pending bills as Paid with one click.
- **Full Invoice Lookup**: Reprint or inspect any past itemized bill.

### 📊 4. Executive Analytics & Reports (`F4`)
- **Real-Time KPI Cards**: Today's Revenue, Today's Bill Count, Lifetime Sales, and Pending Dues.
- **Embedded Visual Charts**:
  - 7-Day Revenue Trend Line Chart (Matplotlib).
  - Top 5 Best-Selling Products Bar Chart.
- **Low Stock Critical Alerts**: Table of all items requiring immediate restocking.

---

## 💻 Launching the Application

### Method 1: One-Click Desktop Launcher
Simply double-click the **`Start_NAS_POS.bat`** file on your Desktop.

### Method 2: From Terminal
```powershell
python "C:\Users\HP\Desktop\NAS-Daily-Needs\app.py"
```

### Method 3: CLI Fallback Mode
The original command-line interface is still 100% operational:
```powershell
python "C:\Users\HP\Desktop\NAS-Daily-Needs\NASDailyneeds.py"
```

---

## 🗄️ Database Architecture

The system connects to MySQL `counter` database:
- `products`: Product catalog, pricing, and live inventory stock.
- `buyer`: Customer records, names, and delivery addresses.
- `bill`: Invoice headers, dates, payment modes, and totals.
- `bill_items`: Itemized line products, unit prices, and quantities for each invoice.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| **`F1`** | Switch to Point of Sale (POS) |
| **`F2`** | Switch to Inventory Control |
| **`F3`** | Switch to Customer Khata CRM |
| **`F4`** | Switch to Executive Analytics |
| **`F5`** | Complete Checkout / Generate Bill |
| **`Esc`** | Close modal dialogs / cancel |

---

## 📦 Project Structure

```text
NAS-Daily-Needs/
├── app.py              # Main PyQt6 Enterprise GUI Application
├── db.py               # Centralized MySQL database abstraction layer
├── NASDailyneeds.py    # Terminal CLI Application fallback
├── schema.sql          # Database DDL & sample data
├── requirements.txt    # Python dependencies (PyQt6, matplotlib, qrcode)
├── Start_NAS_POS.bat   # Desktop 1-click launcher
├── .gitignore          # Git ignore rules
└── README.md           # Documentation
```
