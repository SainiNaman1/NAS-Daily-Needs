import os
import sys
from datetime import date
from io import BytesIO

# Enable High DPI support
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QTextDocument, QColor, QPainter
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QMessageBox, QDialog,
    QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QRadioButton,
    QButtonGroup, QSplitter, QScrollArea, QFileDialog
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import qrcode

import db


# ==============================================================================
# Enterprise Dark Modern Stylesheet (QSS)
# ==============================================================================
ENTERPRISE_STYLE = """
QMainWindow {
    background-color: #0f172a;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #f8fafc;
}

/* Sidebar */
#Sidebar {
    background-color: #1e293b;
    border-right: 1px solid #334155;
}
#StoreLogo {
    font-size: 18px;
    font-weight: bold;
    color: #38bdf8;
    padding: 10px 5px 2px 5px;
}
#StoreTagline {
    font-size: 11px;
    color: #94a3b8;
    padding: 0px 5px 15px 5px;
}
QPushButton.NavBtn, QPushButton[class="NavBtn"] {
    background-color: transparent;
    color: #cbd5e1;
    font-size: 14px;
    font-weight: 500;
    text-align: left;
    padding: 12px 18px;
    border: none;
    border-radius: 8px;
    margin: 4px 10px;
}
QPushButton.NavBtn:hover, QPushButton[class="NavBtn"]:hover {
    background-color: #334155;
    color: #ffffff;
}
QPushButton.NavBtn:checked, QPushButton[class="NavBtn"]:checked {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
}

/* Content Area */
#ContentArea {
    background-color: #0f172a;
}
QFrame.Card, QFrame[class="Card"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 14px;
}
QFrame.KPICard, QFrame[class="KPICard"] {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
}
QLabel.KPITitle, QLabel[class="KPITitle"] {
    font-size: 12px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
QLabel.KPIValue, QLabel[class="KPIValue"] {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
    margin-top: 4px;
}
QLabel.KPISubtext, QLabel[class="KPISubtext"] {
    font-size: 11px;
    color: #38bdf8;
}

/* Headings */
QLabel.PageTitle, QLabel[class="PageTitle"] {
    font-size: 20px;
    font-weight: bold;
    color: #f8fafc;
}
QLabel.SectionTitle, QLabel[class="SectionTitle"] {
    font-size: 15px;
    font-weight: 600;
    color: #e2e8f0;
}

/* Form Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}

/* Tables */
QTableWidget {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    gridline-color: #334155;
    color: #f1f5f9;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 4px 8px;
}
QTableWidget::item:hover {
    background-color: #334155;
}
QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    font-size: 12px;
    font-weight: 600;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #334155;
}

/* Action Buttons */
QPushButton.PrimaryBtn, QPushButton[class="PrimaryBtn"] {
    background-color: #2563eb;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 14px;
    border: none;
    border-radius: 6px;
}
QPushButton.PrimaryBtn:hover, QPushButton[class="PrimaryBtn"]:hover {
    background-color: #1d4ed8;
}
QPushButton.SuccessBtn, QPushButton[class="SuccessBtn"] {
    background-color: #10b981;
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
}
QPushButton.SuccessBtn:hover, QPushButton[class="SuccessBtn"]:hover {
    background-color: #059669;
}
QPushButton.DangerBtn, QPushButton[class="DangerBtn"] {
    background-color: #ef4444;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    padding: 6px 14px;
    border: none;
    border-radius: 6px;
}
QPushButton.DangerBtn:hover, QPushButton[class="DangerBtn"]:hover {
    background-color: #dc2626;
}
QPushButton.SecondaryBtn, QPushButton[class="SecondaryBtn"] {
    background-color: #334155;
    color: #f8fafc;
    font-size: 13px;
    font-weight: 500;
    padding: 6px 12px;
    border: none;
    border-radius: 6px;
}
QPushButton.SecondaryBtn:hover, QPushButton[class="SecondaryBtn"]:hover {
    background-color: #475569;
}

/* Badges */
QLabel.BadgeInStock, QLabel[class="BadgeInStock"] {
    background-color: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid #10b981;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
QLabel.BadgeLowStock, QLabel[class="BadgeLowStock"] {
    background-color: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid #f59e0b;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
QLabel.BadgeOutOfStock, QLabel[class="BadgeOutOfStock"] {
    background-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid #ef4444;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
QLabel.BadgeLowStock {
    background-color: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid #f59e0b;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
QLabel.BadgeOutOfStock {
    background-color: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid #ef4444;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
"""


# ==============================================================================
# Helper Dialogs: Add/Edit Product & UPI QR Code & Invoice
# ==============================================================================
class ProductDialog(QDialog):
    """Dialog for adding or editing products."""
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Edit Product" if product else "Add New Product")
        self.resize(380, 280)
        self.setStyleSheet(ENTERPRISE_STYLE)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.pid_input = QLineEdit()
        self.name_input = QLineEdit()
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.0)
        self.price_input.setValue(10.0)
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(99999)
        self.stock_input.setValue(50)

        if product:
            self.pid_input.setText(str(product['PID']))
            self.pid_input.setEnabled(False)
            self.name_input.setText(str(product['PName']))
            self.price_input.setValue(float(product['Price']))
            self.stock_input.setValue(int(product['stock']))

        form.addRow("Product ID (PID):", self.pid_input)
        form.addRow("Product Name:", self.name_input)
        form.addRow("Price (Rs):", self.price_input)
        form.addRow("Stock Quantity:", self.stock_input)
        layout.addLayout(form)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save Product", self)
        save_btn.setProperty("class", "PrimaryBtn")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "SecondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addLayout(btn_box)

    def save(self):
        pid = self.pid_input.text().strip()
        name = self.name_input.text().strip()
        price = self.price_input.value()
        stock = self.stock_input.value()

        if not pid or not name:
            QMessageBox.warning(self, "Validation Error", "PID and Product Name are required!")
            return

        if self.product:
            ok, msg = db.update_product(pid, name, price, stock)
        else:
            ok, msg = db.add_product(pid, name, price, stock)

        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Error", f"Failed to save product: {msg}")


class UPIQRDialog(QDialog):
    """Dynamic UPI QR Code Dialog."""
    def __init__(self, parent=None, amount=0.0, bill_no=101):
        super().__init__(parent)
        self.setWindowTitle("Scan & Pay via UPI")
        self.resize(340, 420)
        self.setStyleSheet(ENTERPRISE_STYLE)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("UPI Instant Checkout")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        amt_label = QLabel(f"Amount: Rs. {amount:.2f}")
        amt_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981; margin-bottom: 8px;")
        layout.addWidget(amt_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Generate QR code
        vpa = "nasstore@upi"
        upi_url = f"upi://pay?pa={vpa}&pn=NAS%20Daily%20Needs&am={amount:.2f}&cu=INR&tn=Bill%20{bill_no}"
        
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf, format="PNG")
        qimage = QImage.fromData(buf.getvalue())
        pixmap = QPixmap.fromImage(qimage)

        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setStyleSheet("border: 4px solid #ffffff; border-radius: 8px;")
        layout.addWidget(qr_label, alignment=Qt.AlignmentFlag.AlignCenter)

        vpa_label = QLabel(f"UPI ID: {vpa}\nSupported: Google Pay, PhonePe, Paytm, BHIM")
        vpa_label.setStyleSheet("color: #94a3b8; font-size: 11px; text-align: center; margin-top: 6px;")
        vpa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(vpa_label)

        done_btn = QPushButton("Payment Received", self)
        done_btn.setProperty("class", "SuccessBtn")
        done_btn.clicked.connect(self.accept)
        layout.addWidget(done_btn)


class InvoiceDialog(QDialog):
    """Full-featured Invoice & Thermal Receipt Dialog with Print and PDF export."""
    def __init__(self, parent=None, bill_data=None):
        super().__init__(parent)
        self.bill = bill_data
        self.setWindowTitle(f"Invoice - Bill #{bill_data['BillNo']}")
        self.resize(460, 600)
        self.setStyleSheet(ENTERPRISE_STYLE)

        layout = QVBoxLayout(self)

        self.receipt_view = QLabel()
        self.receipt_view.setStyleSheet("""
            background-color: #ffffff;
            color: #000000;
            padding: 20px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
        """)
        self.receipt_view.setTextFormat(Qt.TextFormat.RichText)
        self.receipt_view.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.html_content = self.generate_html()
        self.receipt_view.setText(self.html_content)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.receipt_view)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        print_btn = QPushButton("🖨️ Print Invoice", self)
        print_btn.setProperty("class", "PrimaryBtn")
        print_btn.clicked.connect(self.print_receipt)

        pdf_btn = QPushButton("💾 Save PDF", self)
        pdf_btn.setProperty("class", "SecondaryBtn")
        pdf_btn.clicked.connect(self.save_pdf)

        close_btn = QPushButton("Close", self)
        close_btn.setProperty("class", "SecondaryBtn")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(pdf_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def generate_html(self):
        b = self.bill
        items_html = ""
        for it in b.get('items', []):
            name = it.get('PName', '')[:18]
            price = float(it.get('price', 0))
            qty = int(it.get('quantity', 1))
            total = float(it.get('item_total', 0))
            items_html += f"""
            <tr>
                <td style='padding: 4px 0;'>{name}</td>
                <td align='center'>{qty}</td>
                <td align='right'>{price:.2f}</td>
                <td align='right'>{total:.2f}</td>
            </tr>
            """

        c_name = b.get('name') or "Walk-in Customer"
        c_mob = b.get('mobile') or "N/A"
        date_str = str(b.get('date', date.today()))

        html = f"""
        <div style='text-align: center;'>
            <h2 style='margin:0; font-size: 18px;'>NAS DAILY NEEDS</h2>
            <p style='margin:2px; font-size:11px;'>Daily Groceries & Essentials</p>
            <p style='margin:2px; font-size:10px;'>Ph: +91 98765 43210 | GSTIN: 07AAAAA0000A1Z5</p>
            <hr style='border: none; border-top: 1px dashed #000; margin: 8px 0;'>
        </div>
        <div style='font-size: 11px;'>
            <b>Bill No:</b> #{b['BillNo']} &nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> {date_str}<br>
            <b>Customer:</b> {c_name}<br>
            <b>Mobile:</b> {c_mob}<br>
            <b>Payment:</b> {b['mode']} ({b['status']})
            <hr style='border: none; border-top: 1px dashed #000; margin: 8px 0;'>
        </div>
        <table width='100%' style='font-size: 11px; border-collapse: collapse;'>
            <thead>
                <tr style='border-bottom: 1px solid #000;'>
                    <th align='left'>Item</th>
                    <th align='center'>Qty</th>
                    <th align='right'>Price</th>
                    <th align='right'>Total</th>
                </tr>
            </thead>
            <tbody>
                {items_html}
            </tbody>
        </table>
        <hr style='border: none; border-top: 1px dashed #000; margin: 8px 0;'>
        <div style='text-align: right; font-size: 14px;'>
            <b>GRAND TOTAL: Rs. {float(b['total']):.2f}</b>
        </div>
        <hr style='border: none; border-top: 1px dashed #000; margin: 8px 0;'>
        <div style='text-align: center; font-size: 11px; margin-top: 8px;'>
            Thank you for shopping with us!<br>
            *** Visit Again ***
        </div>
        """
        return html

    def print_receipt(self):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print(printer)

    def save_pdf(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Invoice as PDF", f"Invoice_{self.bill['BillNo']}.pdf", "PDF Files (*.pdf)")
        if filename:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(filename)
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print(printer)
            QMessageBox.information(self, "PDF Saved", f"Invoice successfully saved to:\n{filename}")


# ==============================================================================
# Module 1: POS Terminal View
# ==============================================================================
class POSView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart = []  # [{pid, name, price, qty, subtotal, max_stock}]
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -----------------------------
        # Left Panel: Product Catalog
        # -----------------------------
        left_frame = QFrame()
        left_frame.setProperty("class", "Card")
        left_layout = QVBoxLayout(left_frame)

        left_header = QHBoxLayout()
        cat_title = QLabel("Product Catalog")
        cat_title.setProperty("class", "SectionTitle")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name or PID...")
        self.search_input.textChanged.connect(self.filter_products)
        left_header.addWidget(cat_title)
        left_header.addStretch()
        left_header.addWidget(self.search_input)
        left_layout.addLayout(left_header)

        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(5)
        self.prod_table.setHorizontalHeaderLabels(["PID", "Product Name", "Price (Rs)", "Stock", "Action"])
        self.prod_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.prod_table.setColumnWidth(0, 75)
        self.prod_table.setColumnWidth(2, 95)
        self.prod_table.setColumnWidth(3, 75)
        self.prod_table.setColumnWidth(4, 110)
        self.prod_table.verticalHeader().setDefaultSectionSize(44)
        self.prod_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.prod_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.prod_table.doubleClicked.connect(self.on_table_double_clicked)
        left_layout.addWidget(self.prod_table)

        main_layout.addWidget(left_frame, stretch=6)

        # -----------------------------
        # Right Panel: Active Cart & Billing
        # -----------------------------
        right_frame = QFrame()
        right_frame.setProperty("class", "Card")
        right_layout = QVBoxLayout(right_frame)

        cart_header = QHBoxLayout()
        cart_title = QLabel("Checkout Counter")
        cart_title.setProperty("class", "SectionTitle")
        self.bill_no_label = QLabel("Bill #101")
        self.bill_no_label.setStyleSheet("font-weight: bold; color: #38bdf8;")
        cart_header.addWidget(cart_title)
        cart_header.addStretch()
        cart_header.addWidget(self.bill_no_label)
        right_layout.addLayout(cart_header)

        # Customer Info Section
        cust_box = QFormLayout()
        cust_box.setContentsMargins(0, 8, 0, 8)
        self.cust_mobile_input = QLineEdit()
        self.cust_mobile_input.setPlaceholderText("10-Digit Mobile Number")
        self.cust_mobile_input.textChanged.connect(self.on_mobile_changed)
        
        self.cust_name_input = QLineEdit()
        self.cust_name_input.setPlaceholderText("Customer Name")
        
        cust_box.addRow("Mobile:", self.cust_mobile_input)
        cust_box.addRow("Name:", self.cust_name_input)
        right_layout.addLayout(cust_box)

        # Cart Table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Price", "Qty", "Total", "Action"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cart_table.setColumnWidth(4, 75)
        self.cart_table.verticalHeader().setDefaultSectionSize(40)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.cart_table)

        # Payment & Summary Frame
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background-color: #0f172a; border-radius: 8px; padding: 10px;")
        sum_layout = QVBoxLayout(summary_frame)

        # Payment Mode radio buttons
        pay_box = QHBoxLayout()
        pay_label = QLabel("Payment:")
        pay_label.setStyleSheet("font-size: 12px; color: #94a3b8;")
        self.rb_cash = QRadioButton("Cash")
        self.rb_upi = QRadioButton("UPI")
        self.rb_card = QRadioButton("Card")
        self.rb_later = QRadioButton("PayLater")
        self.rb_cash.setChecked(True)

        self.pay_group = QButtonGroup(self)
        self.pay_group.addButton(self.rb_cash, 1)
        self.pay_group.addButton(self.rb_upi, 2)
        self.pay_group.addButton(self.rb_card, 3)
        self.pay_group.addButton(self.rb_later, 4)

        pay_box.addWidget(pay_label)
        pay_box.addWidget(self.rb_cash)
        pay_box.addWidget(self.rb_upi)
        pay_box.addWidget(self.rb_card)
        pay_box.addWidget(self.rb_later)
        sum_layout.addLayout(pay_box)

        # QR Button (visible if UPI)
        self.upi_btn = QPushButton("📱 Show UPI QR Code", self)
        self.upi_btn.setProperty("class", "PrimaryBtn")
        self.upi_btn.clicked.connect(self.show_upi_qr)
        self.upi_btn.setVisible(False)
        self.pay_group.idClicked.connect(lambda id: self.upi_btn.setVisible(id == 2))
        sum_layout.addWidget(self.upi_btn)

        # Grand Total Display
        total_box = QHBoxLayout()
        total_lbl = QLabel("GRAND TOTAL:")
        total_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        self.total_val_lbl = QLabel("Rs. 0.00")
        self.total_val_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #10b981;")
        total_box.addWidget(total_lbl)
        total_box.addStretch()
        total_box.addWidget(self.total_val_lbl)
        sum_layout.addLayout(total_box)

        right_layout.addWidget(summary_frame)

        # Checkout & Clear Buttons
        btn_box = QHBoxLayout()
        clear_btn = QPushButton("Clear Cart", self)
        clear_btn.setProperty("class", "SecondaryBtn")
        clear_btn.clicked.connect(self.clear_cart)

        checkout_btn = QPushButton("⚡ Complete Checkout (F5)", self)
        checkout_btn.setProperty("class", "SuccessBtn")
        checkout_btn.clicked.connect(self.process_sale)

        btn_box.addWidget(clear_btn)
        btn_box.addWidget(checkout_btn)
        right_layout.addLayout(btn_box)

        main_layout.addWidget(right_frame, stretch=5)

        self.load_products()
        self.update_bill_no()

    def update_bill_no(self):
        self.next_bill = db.get_next_bill_no()
        self.bill_no_label.setText(f"Bill #{self.next_bill}")

    def load_products(self, search=""):
        products = db.get_all_products(search)
        self.prod_table.setRowCount(len(products))

        for row, p in enumerate(products):
            pid_item = QTableWidgetItem(str(p['PID']))
            name_item = QTableWidgetItem(str(p['PName']))
            price_item = QTableWidgetItem(f"{float(p['Price']):.2f}")
            stock_item = QTableWidgetItem(str(p['stock']))

            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            self.prod_table.setItem(row, 0, pid_item)
            self.prod_table.setItem(row, 1, name_item)
            self.prod_table.setItem(row, 2, price_item)
            self.prod_table.setItem(row, 3, stock_item)

            # Action button inside layout container for perfect sizing
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            add_btn = QPushButton("+ Add")
            add_btn.setMinimumHeight(28)
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    font-size: 12px;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:disabled {
                    background-color: #334155;
                    color: #64748b;
                }
            """)
            add_btn.setEnabled(p['stock'] > 0)
            add_btn.clicked.connect(lambda checked, prod=p: self.add_to_cart(prod))
            btn_layout.addWidget(add_btn)
            self.prod_table.setCellWidget(row, 4, btn_container)

    def filter_products(self, text):
        self.load_products(text.strip())

    def on_table_double_clicked(self, index):
        row = index.row()
        pid = self.prod_table.item(row, 0).text()
        prods = [p for p in db.get_all_products() if p['PID'] == pid]
        if prods and prods[0]['stock'] > 0:
            self.add_to_cart(prods[0])

    def add_to_cart(self, prod):
        pid = prod['PID']
        existing = next((item for item in self.cart if item['pid'] == pid), None)
        if existing:
            if existing['qty'] < prod['stock']:
                existing['qty'] += 1
                existing['subtotal'] = existing['qty'] * existing['price']
            else:
                QMessageBox.warning(self, "Stock Limit", f"Cannot add more! Only {prod['stock']} available in stock.")
                return
        else:
            self.cart.append({
                'pid': pid,
                'name': prod['PName'],
                'price': float(prod['Price']),
                'qty': 1,
                'subtotal': float(prod['Price']),
                'max_stock': prod['stock']
            })
        self.render_cart()

    def render_cart(self):
        self.cart_table.setRowCount(len(self.cart))
        grand_total = 0.0

        for row, item in enumerate(self.cart):
            grand_total += item['subtotal']
            name_item = QTableWidgetItem(item['name'])
            price_item = QTableWidgetItem(f"{item['price']:.2f}")
            tot_item = QTableWidgetItem(f"{item['subtotal']:.2f}")

            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tot_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Quantity control widget
            qty_widget = QWidget()
            qty_layout = QHBoxLayout(qty_widget)
            qty_layout.setContentsMargins(0, 0, 0, 0)
            qty_layout.setSpacing(2)

            minus_btn = QPushButton("-")
            minus_btn.setFixedSize(22, 22)
            minus_btn.setProperty("class", "SecondaryBtn")
            minus_btn.clicked.connect(lambda checked, idx=row: self.update_qty(idx, -1))

            qty_lbl = QLabel(str(item['qty']))
            qty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_lbl.setFixedWidth(24)

            plus_btn = QPushButton("+")
            plus_btn.setFixedSize(22, 22)
            plus_btn.setProperty("class", "SecondaryBtn")
            plus_btn.clicked.connect(lambda checked, idx=row: self.update_qty(idx, 1))

            qty_layout.addWidget(minus_btn)
            qty_layout.addWidget(qty_lbl)
            qty_layout.addWidget(plus_btn)

            # Delete button container
            del_container = QWidget()
            del_layout = QHBoxLayout(del_container)
            del_layout.setContentsMargins(4, 2, 4, 2)

            del_btn = QPushButton("✕")
            del_btn.setFixedSize(26, 26)
            del_btn.setToolTip("Remove from cart")
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            del_btn.clicked.connect(lambda checked, idx=row: self.remove_item(idx))
            del_layout.addWidget(del_btn)

            self.cart_table.setItem(row, 0, name_item)
            self.cart_table.setItem(row, 1, price_item)
            self.cart_table.setCellWidget(row, 2, qty_widget)
            self.cart_table.setItem(row, 3, tot_item)
            self.cart_table.setCellWidget(row, 4, del_container)

        self.total_val_lbl.setText(f"Rs. {grand_total:.2f}")

    def update_qty(self, idx, delta):
        item = self.cart[idx]
        new_qty = item['qty'] + delta
        if new_qty <= 0:
            self.remove_item(idx)
        elif new_qty > item['max_stock']:
            QMessageBox.warning(self, "Stock Limit", f"Only {item['max_stock']} units available in stock!")
        else:
            item['qty'] = new_qty
            item['subtotal'] = item['qty'] * item['price']
            self.render_cart()

    def remove_item(self, idx):
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self.render_cart()

    def clear_cart(self):
        self.cart = []
        self.render_cart()

    def on_mobile_changed(self, text):
        clean = ''.join(filter(str.isdigit, text))
        if len(clean) == 10:
            cust = db.get_customer(int(clean))
            if cust:
                self.cust_name_input.setText(cust['name'])

    def show_upi_qr(self):
        total = sum(c['subtotal'] for c in self.cart)
        if total <= 0:
            QMessageBox.warning(self, "Empty Cart", "Add items to cart before generating QR code!")
            return
        qr_dialog = UPIQRDialog(self, total, self.next_bill)
        qr_dialog.exec()

    def process_sale(self):
        if not self.cart:
            QMessageBox.warning(self, "Empty Cart", "Cannot checkout an empty cart!")
            return

        mob_str = self.cust_mobile_input.text().strip()
        if not mob_str.isdigit() or len(mob_str) != 10:
            QMessageBox.warning(self, "Invalid Mobile", "Please enter a valid 10-digit customer mobile number!")
            return

        cust_mobile = int(mob_str)
        cust_name = self.cust_name_input.text().strip() or "Walk-in Customer"
        cust_addr = "Local"

        # Determine payment mode & status
        mode_id = self.pay_group.checkedId()
        mode_map = {1: "Cash", 2: "UPI", 3: "Card", 4: "PayLater"}
        mode = mode_map.get(mode_id, "Cash")
        status = "Pending" if mode == "PayLater" else "Paid"
        total = sum(c['subtotal'] for c in self.cart)

        ok, msg = db.process_checkout(
            self.next_bill, cust_mobile, cust_name, cust_addr,
            mode, status, self.cart, total
        )

        if ok:
            # Fetch generated bill details and show Invoice
            bill_data = db.get_bill_details(self.next_bill)
            invoice = InvoiceDialog(self, bill_data)
            invoice.exec()

            # Reset cart and refresh
            self.clear_cart()
            self.cust_mobile_input.clear()
            self.cust_name_input.clear()
            self.load_products()
            self.update_bill_no()
        else:
            QMessageBox.critical(self, "Checkout Failed", f"Error generating bill: {msg}")


# ==============================================================================
# Module 2: Inventory & Stock Management View
# ==============================================================================
class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        card = QFrame()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)

        # Toolbar
        bar = QHBoxLayout()
        title = QLabel("Inventory Control & Catalog")
        title.setProperty("class", "SectionTitle")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Filter products...")
        self.search_box.textChanged.connect(self.refresh_table)

        add_btn = QPushButton("➕ Add Product", self)
        add_btn.setProperty("class", "PrimaryBtn")
        add_btn.clicked.connect(self.add_product)

        edit_btn = QPushButton("✏️ Edit", self)
        edit_btn.setProperty("class", "SecondaryBtn")
        edit_btn.clicked.connect(self.edit_selected)

        del_btn = QPushButton("🗑️ Delete", self)
        del_btn.setProperty("class", "DangerBtn")
        del_btn.clicked.connect(self.delete_selected)

        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(self.search_box)
        bar.addWidget(add_btn)
        bar.addWidget(edit_btn)
        bar.addWidget(del_btn)
        card_layout.addLayout(bar)

        # Products Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["PID", "Product Name", "Unit Price (Rs)", "Stock", "Inventory Value", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        card_layout.addWidget(self.table)

        layout.addWidget(card)
        self.refresh_table()

    def refresh_table(self):
        term = self.search_box.text().strip()
        products = db.get_all_products(term)
        self.table.setRowCount(len(products))

        for row, p in enumerate(products):
            pid_item = QTableWidgetItem(str(p['PID']))
            name_item = QTableWidgetItem(str(p['PName']))
            price = float(p['Price'])
            stock = int(p['stock'])
            val = price * stock

            price_item = QTableWidgetItem(f"{price:.2f}")
            stock_item = QTableWidgetItem(str(stock))
            val_item = QTableWidgetItem(f"Rs. {val:.2f}")

            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.table.setItem(row, 0, pid_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, price_item)
            self.table.setItem(row, 3, stock_item)
            self.table.setItem(row, 4, val_item)

            # Badge for status
            badge = QLabel()
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if stock == 0:
                badge.setText("OUT OF STOCK")
                badge.setProperty("class", "BadgeOutOfStock")
            elif stock <= 5:
                badge.setText(f"LOW ({stock})")
                badge.setProperty("class", "BadgeLowStock")
            else:
                badge.setText("In Stock")
                badge.setProperty("class", "BadgeInStock")

            self.table.setCellWidget(row, 5, badge)

    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_table()

    def edit_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Product", "Please select a product from the table to edit.")
            return
        pid = self.table.item(row, 0).text()
        prods = [p for p in db.get_all_products() if p['PID'] == pid]
        if prods:
            dialog = ProductDialog(self, prods[0])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_table()

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Product", "Please select a product to delete.")
            return
        pid = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Permanently delete '{name}' ({pid})?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            ok, msg = db.delete_product(pid)
            if ok:
                self.refresh_table()
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete: {msg}")


# ==============================================================================
# Module 3: Customer Directory & Khata CRM View
# ==============================================================================
class CustomerCRMView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        card = QFrame()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)

        # Toolbar
        bar = QHBoxLayout()
        title = QLabel("Customer Directory & Khata Ledger")
        title.setProperty("class", "SectionTitle")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search by customer name or phone...")
        self.search_box.textChanged.connect(self.refresh_customers)

        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(self.search_box)
        card_layout.addLayout(bar)

        # Splitter: Left Customer List, Right Purchase History
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Customer Table
        self.cust_table = QTableWidget()
        self.cust_table.setColumnCount(5)
        self.cust_table.setHorizontalHeaderLabels(["Name", "Mobile", "Address", "Lifetime Spend", "Pending Due"])
        self.cust_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.cust_table.verticalHeader().setDefaultSectionSize(42)
        self.cust_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cust_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cust_table.itemSelectionChanged.connect(self.on_customer_selected)
        splitter.addWidget(self.cust_table)

        # Right History Card
        self.history_frame = QFrame()
        self.history_frame.setStyleSheet("background-color: #0f172a; border-radius: 8px; padding: 12px;")
        hist_layout = QVBoxLayout(self.history_frame)

        self.hist_header = QLabel("Select a customer to view purchase history")
        self.hist_header.setStyleSheet("font-size: 14px; font-weight: bold; color: #38bdf8;")
        hist_layout.addWidget(self.hist_header)

        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(5)
        self.bills_table.setHorizontalHeaderLabels(["Bill #", "Date", "Mode", "Status", "Total (Rs)"])
        self.bills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.bills_table.verticalHeader().setDefaultSectionSize(40)
        self.bills_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bills_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        hist_layout.addWidget(self.bills_table)

        hist_btn_bar = QHBoxLayout()
        self.view_bill_btn = QPushButton("🧾 View Full Invoice", self)
        self.view_bill_btn.setProperty("class", "PrimaryBtn")
        self.view_bill_btn.clicked.connect(self.view_selected_invoice)

        self.settle_btn = QPushButton("💳 Settle Pending Due", self)
        self.settle_btn.setProperty("class", "SuccessBtn")
        self.settle_btn.clicked.connect(self.settle_selected_bill)

        hist_btn_bar.addWidget(self.view_bill_btn)
        hist_btn_bar.addWidget(self.settle_btn)
        hist_layout.addLayout(hist_btn_bar)

        splitter.addWidget(self.history_frame)
        splitter.setSizes([600, 480])

        card_layout.addWidget(splitter)
        layout.addWidget(card)

        self.refresh_customers()

    def refresh_customers(self):
        term = self.search_box.text().strip()
        customers = db.get_all_customers(term)
        self.cust_table.setRowCount(len(customers))

        for row, c in enumerate(customers):
            name_item = QTableWidgetItem(str(c['name']))
            mob_item = QTableWidgetItem(str(c['mobile']))
            addr_item = QTableWidgetItem(str(c['address']))
            spend_item = QTableWidgetItem(f"Rs. {float(c['total_spent']):.2f}")
            due_item = QTableWidgetItem(f"Rs. {float(c['pending_dues']):.2f}")

            spend_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            due_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if float(c['pending_dues']) > 0:
                due_item.setForeground(QColor("#f59e0b"))

            self.cust_table.setItem(row, 0, name_item)
            self.cust_table.setItem(row, 1, mob_item)
            self.cust_table.setItem(row, 2, addr_item)
            self.cust_table.setItem(row, 3, spend_item)
            self.cust_table.setItem(row, 4, due_item)

    def on_customer_selected(self):
        row = self.cust_table.currentRow()
        if row < 0:
            return
        mob_str = self.cust_table.item(row, 1).text()
        name_str = self.cust_table.item(row, 0).text()
        self.hist_header.setText(f"Purchases for: {name_str} ({mob_str})")

        conn = db.get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT BillNo, `date`, mode, status, total FROM bill WHERE mobile = %s ORDER BY `date` DESC", (int(mob_str),))
        bills = cur.fetchall()
        cur.close()
        conn.close()

        self.bills_table.setRowCount(len(bills))
        for r, b in enumerate(bills):
            bno_item = QTableWidgetItem(str(b['BillNo']))
            date_item = QTableWidgetItem(str(b['date']))
            mode_item = QTableWidgetItem(str(b['mode']))
            stat_item = QTableWidgetItem(str(b['status']))
            tot_item = QTableWidgetItem(f"{float(b['total']):.2f}")

            tot_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if b['status'] == "Pending":
                stat_item.setForeground(QColor("#ef4444"))
            else:
                stat_item.setForeground(QColor("#10b981"))

            self.bills_table.setItem(r, 0, bno_item)
            self.bills_table.setItem(r, 1, date_item)
            self.bills_table.setItem(r, 2, mode_item)
            self.bills_table.setItem(r, 3, stat_item)
            self.bills_table.setItem(r, 4, tot_item)

    def view_selected_invoice(self):
        row = self.bills_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Bill", "Please select a bill from the history table.")
            return
        bno = int(self.bills_table.item(row, 0).text())
        bill_data = db.get_bill_details(bno)
        if bill_data:
            inv = InvoiceDialog(self, bill_data)
            inv.exec()

    def settle_selected_bill(self):
        row = self.bills_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Bill", "Please select a pending bill to settle.")
            return
        status = self.bills_table.item(row, 3).text()
        bno = int(self.bills_table.item(row, 0).text())
        if status != "Pending":
            QMessageBox.information(self, "Already Settled", "This bill is already marked as Paid.")
            return

        confirm = QMessageBox.question(self, "Confirm Settlement", f"Mark Bill #{bno} as Paid?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if db.settle_bill_due(bno):
                QMessageBox.information(self, "Settled", f"Bill #{bno} settled successfully.")
                self.on_customer_selected()
                self.refresh_customers()


# ==============================================================================
# Module 4: Analytics Dashboard View
# ==============================================================================
class AnalyticsDashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header
        bar = QHBoxLayout()
        title = QLabel("Executive Analytics Dashboard")
        title.setProperty("class", "PageTitle")
        refresh_btn = QPushButton("🔄 Refresh Analytics", self)
        refresh_btn.setProperty("class", "SecondaryBtn")
        refresh_btn.clicked.connect(self.refresh_dashboard)

        bar.addWidget(title)
        bar.addStretch()
        bar.addWidget(refresh_btn)
        layout.addLayout(bar)

        # Top KPI Stat Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(14)

        self.kpi1 = self.create_kpi_card("TODAY'S REVENUE", "Rs. 0.00", "0 bills today")
        self.kpi2 = self.create_kpi_card("LIFETIME SALES", "Rs. 0.00", "0 total orders")
        self.kpi3 = self.create_kpi_card("PENDING DUES", "Rs. 0.00", "0 unpaid tabs")
        self.kpi4 = self.create_kpi_card("LOW STOCK ITEMS", "0 items", "Action required")

        kpi_layout.addWidget(self.kpi1)
        kpi_layout.addWidget(self.kpi2)
        kpi_layout.addWidget(self.kpi3)
        kpi_layout.addWidget(self.kpi4)
        layout.addLayout(kpi_layout)

        # Embedded Charts Section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(14)

        # Chart 1: 7-Day Revenue Trend
        self.trend_card = QFrame()
        self.trend_card.setProperty("class", "Card")
        trend_layout = QVBoxLayout(self.trend_card)
        t_label = QLabel("7-Day Revenue Trend (Rs)")
        t_label.setProperty("class", "SectionTitle")
        trend_layout.addWidget(t_label)

        self.trend_figure = Figure(figsize=(5, 3.2), facecolor="#1e293b")
        self.trend_canvas = FigureCanvas(self.trend_figure)
        trend_layout.addWidget(self.trend_canvas)
        charts_layout.addWidget(self.trend_card, stretch=6)

        # Chart 2: Top 5 Best Sellers
        self.top_card = QFrame()
        self.top_card.setProperty("class", "Card")
        top_layout = QVBoxLayout(self.top_card)
        top_label = QLabel("Top 5 Best-Selling Products")
        top_label.setProperty("class", "SectionTitle")
        top_layout.addWidget(top_label)

        self.top_figure = Figure(figsize=(5, 3.2), facecolor="#1e293b")
        self.top_canvas = FigureCanvas(self.top_figure)
        top_layout.addWidget(self.top_canvas)
        charts_layout.addWidget(self.top_card, stretch=5)

        layout.addLayout(charts_layout)
        self.refresh_dashboard()

    def create_kpi_card(self, title, val, sub):
        card = QFrame()
        card.setProperty("class", "KPICard")
        l = QVBoxLayout(card)
        l.setSpacing(4)
        t = QLabel(title)
        t.setProperty("class", "KPITitle")
        v = QLabel(val)
        v.setProperty("class", "KPIValue")
        s = QLabel(sub)
        s.setProperty("class", "KPISubtext")
        l.addWidget(t)
        l.addWidget(v)
        l.addWidget(s)
        card.value_label = v
        card.sub_label = s
        return card

    def refresh_dashboard(self):
        m = db.get_analytics_metrics()
        if not m:
            return

        self.kpi1.value_label.setText(f"Rs. {m['today_revenue']:.2f}")
        self.kpi1.sub_label.setText(f"{m['today_bills']} bills generated today")

        self.kpi2.value_label.setText(f"Rs. {m['lifetime_revenue']:.2f}")
        self.kpi2.sub_label.setText(f"{m['lifetime_bills']} lifetime orders")

        self.kpi3.value_label.setText(f"Rs. {m['pending_dues_total']:.2f}")
        self.kpi3.sub_label.setText(f"{m['pending_dues_count']} pending tabs")

        self.kpi4.value_label.setText(f"{m['low_stock_count']} Products")
        self.kpi4.sub_label.setText("Restock recommended" if m['low_stock_count'] > 0 else "All stock healthy")

        # 1. Render Trend Chart
        self.trend_figure.clear()
        ax1 = self.trend_figure.add_subplot(111)
        ax1.set_facecolor("#0f172a")
        days = m['trend_days']
        revs = m['trend_revs']
        ax1.plot(days, revs, marker='o', color='#38bdf8', linewidth=2.5, markersize=6)
        ax1.fill_between(days, revs, color='#38bdf8', alpha=0.15)
        ax1.tick_params(colors='#94a3b8', labelsize=9)
        ax1.spines['bottom'].set_color('#334155')
        ax1.spines['left'].set_color('#334155')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(True, linestyle='--', alpha=0.15, color='#ffffff')
        self.trend_figure.tight_layout()
        self.trend_canvas.draw()

        # 2. Render Top Products Chart
        self.top_figure.clear()
        ax2 = self.top_figure.add_subplot(111)
        ax2.set_facecolor("#0f172a")

        top_p = m['top_products']
        if top_p:
            names = [p['PName'][:14] for p in reversed(top_p)]
            sales = [int(p['sold']) for p in reversed(top_p)]
            bars = ax2.barh(names, sales, color='#10b981', height=0.55)
            ax2.bar_label(bars, padding=4, color='#ffffff', fontsize=9)
        else:
            ax2.text(0.5, 0.5, "No Sales Data Yet", color='#94a3b8', ha='center', va='center')

        ax2.tick_params(colors='#94a3b8', labelsize=9)
        ax2.spines['bottom'].set_color('#334155')
        ax2.spines['left'].set_color('#334155')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        self.top_figure.tight_layout()
        self.top_canvas.draw()


# ==============================================================================
# Main Enterprise Window
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NAS Daily Needs - Enterprise POS & Retail ERP")
        self.resize(1300, 820)
        self.setStyleSheet(ENTERPRISE_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # -----------------------------
        # Left Sidebar Navigation
        # -----------------------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(8, 16, 8, 16)
        s_layout.setSpacing(6)

        # Branding
        logo = QLabel("NAS DAILY NEEDS")
        logo.setObjectName("StoreLogo")
        tagline = QLabel("Retail POS & ERP System")
        tagline.setObjectName("StoreTagline")
        s_layout.addWidget(logo)
        s_layout.addWidget(tagline)

        # Nav Buttons
        self.btn_pos = QPushButton("🛒  Point of Sale (F1)")
        self.btn_inv = QPushButton("📦  Inventory (F2)")
        self.btn_crm = QPushButton("👥  Customers (F3)")
        self.btn_ana = QPushButton("📊  Analytics (F4)")

        for btn in [self.btn_pos, self.btn_inv, self.btn_crm, self.btn_ana]:
            btn.setProperty("class", "NavBtn")
            btn.setCheckable(True)
            s_layout.addWidget(btn)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_group.addButton(self.btn_pos, 0)
        self.nav_group.addButton(self.btn_inv, 1)
        self.nav_group.addButton(self.btn_crm, 2)
        self.nav_group.addButton(self.btn_ana, 3)
        self.nav_group.idClicked.connect(self.switch_page)

        self.btn_pos.setChecked(True)

        s_layout.addStretch()

        # Database Status Badge
        db_badge = QFrame()
        db_badge.setStyleSheet("background-color: #0f172a; border-radius: 6px; padding: 8px;")
        db_layout = QHBoxLayout(db_badge)
        db_layout.setContentsMargins(6, 6, 6, 6)
        dot = QLabel("●")
        dot.setStyleSheet("color: #10b981; font-size: 14px;")
        status_txt = QLabel("MySQL Connected\nDatabase: counter")
        status_txt.setStyleSheet("color: #94a3b8; font-size: 10px;")
        db_layout.addWidget(dot)
        db_layout.addWidget(status_txt)
        s_layout.addWidget(db_badge)

        main_layout.addWidget(sidebar)

        # -----------------------------
        # Central Stacked Views
        # -----------------------------
        self.stack = QStackedWidget()
        self.stack.setObjectName("ContentArea")

        self.pos_view = POSView()
        self.inv_view = InventoryView()
        self.crm_view = CustomerCRMView()
        self.ana_view = AnalyticsDashboardView()

        self.stack.addWidget(self.pos_view)
        self.stack.addWidget(self.inv_view)
        self.stack.addWidget(self.crm_view)
        self.stack.addWidget(self.ana_view)

        main_layout.addWidget(self.stack)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.pos_view.load_products()
            self.pos_view.update_bill_no()
        elif index == 1:
            self.inv_view.refresh_table()
        elif index == 2:
            self.crm_view.refresh_customers()
        elif index == 3:
            self.ana_view.refresh_dashboard()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_F1:
            self.btn_pos.setChecked(True)
            self.switch_page(0)
        elif key == Qt.Key.Key_F2:
            self.btn_inv.setChecked(True)
            self.switch_page(1)
        elif key == Qt.Key.Key_F3:
            self.btn_crm.setChecked(True)
            self.switch_page(2)
        elif key == Qt.Key.Key_F4:
            self.btn_ana.setChecked(True)
            self.switch_page(3)
        elif key == Qt.Key.Key_F5 and self.stack.currentIndex() == 0:
            self.pos_view.process_sale()
        else:
            super().keyPressEvent(event)


def main():
    # Initialize DB first
    db.init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
