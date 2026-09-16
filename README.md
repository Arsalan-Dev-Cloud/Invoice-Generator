# Invoice Generator

A Python-based Invoice Generator web application built with **Flask**, **SQLite**, **ReportLab**, **HTML**, **CSS**, and **JavaScript**.

The application allows users to create invoices with multiple products, automatically calculate GST, generate PDF invoices, store invoice records in SQLite, view invoice history, download invoices, delete invoices, and analyze invoice data through a dashboard.

---

# 1. Project Overview

The Invoice Generator provides a complete invoice management workflow:

```text
Create Invoice
      ↓
Add Multiple Products
      ↓
Calculate Subtotal
      ↓
Calculate GST
      ↓
Calculate Grand Total
      ↓
Generate PDF
      ↓
Save Invoice to SQLite
      ↓
Invoice History
      ↓
View Invoice Details
      ↓
Download PDF
      ↓
Dashboard & Analytics
```

---

# 2. Technologies Used

## Backend

* Python
* Flask
* SQLite
* ReportLab

## Frontend

* HTML5
* CSS3
* JavaScript

## Data & Analytics

* SQLite
* SQL queries
* Chart.js

## Development Tools

* Visual Studio Code
* PowerShell
* Python Virtual Environment
* Git / GitHub

---

# 3. Main Features

## Invoice Management

* Create invoices
* Add multiple products
* Delete invoice items before generating
* Automatic invoice numbering
* Customer information
* Product quantity
* Product price
* Automatic item total calculation

## Tax Calculation

The application currently uses:

```text
GST = 18%
```

Calculation:

```text
Subtotal = Sum of all item totals

GST = Subtotal × 18 / 100

Grand Total = Subtotal + GST
```

## PDF Generation

Each invoice is automatically generated as a PDF.

Example:

```text
INV-001.pdf
INV-002.pdf
INV-003.pdf
```

PDF files are stored inside:

```text
invoices/
```

## Database

SQLite stores:

* Invoice information
* Customer information
* Invoice date
* Subtotal
* GST
* Grand total
* Product information
* Quantity
* Price
* Item total

## Invoice History

The application provides:

* Invoice number
* Customer name
* Customer email
* Date
* Subtotal
* GST
* Grand total
* View Details
* Delete Invoice

## Invoice Details

Each invoice has a dedicated details page containing:

* Customer information
* Invoice date
* Products
* Quantities
* Prices
* Item totals
* Subtotal
* GST
* Grand total

## Dashboard

The dashboard provides:

* Total invoices
* Total revenue
* Total GST
* Average invoice value
* Monthly statistics
* Monthly revenue chart
* Product sales statistics
* Product revenue chart

---

# 4. Requirements

Before installing the project, make sure the following are installed.

## Python

Recommended Python version:

```text
Python 3.13
```

The project was developed using a Python virtual environment.

Check your Python version:

```powershell
python --version
```

Example:

```text
Python 3.13.x
```

You can also check:

```powershell
py --version
```

---

# 5. Create the Project Folder

Example:

```text
E:\Invoice-Generator
```

Open PowerShell and run:

```powershell
cd E:\
mkdir Invoice-Generator
cd Invoice-Generator
```

If the project folder already exists, simply run:

```powershell
cd E:\Invoice-Generator
```

---

# 6. Create Python Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

This creates:

```text
E:\Invoice-Generator\.venv
```

The virtual environment keeps the project's Python packages separate from the global Python installation.

---

# 7. Activate the Virtual Environment

In PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, PowerShell should show:

```text
(.venv) PS E:\Invoice-Generator>
```

This means the virtual environment is active.

---

# 8. If PowerShell Blocks Activation

If PowerShell shows an execution-policy error, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

The setting only applies to the current PowerShell session.

---

# 9. Verify the Virtual Environment Path

This is important.

Run:

```powershell
python -c "import sys; print(sys.executable)"
```

The result should be:

```text
E:\Invoice-Generator\.venv\Scripts\python.exe
```

This confirms that Python is coming from the project's virtual environment.

You can also run:

```powershell
where.exe python
```

The `.venv` Python path should appear first.

---

# 10. Configure VS Code Python Interpreter

Open the project in Visual Studio Code.

From PowerShell:

```powershell
code .
```

In VS Code:

```text
Ctrl + Shift + P
```

Search:

```text
Python: Select Interpreter
```

Select:

```text
E:\Invoice-Generator\.venv\Scripts\python.exe
```

This is the interpreter that VS Code should use for the project.

You should see something similar to:

```text
Python 3.x.x ('.venv': venv)
```

---

# 11. Install Required Python Packages

Make sure the virtual environment is activated.

Then upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install Flask:

```powershell
pip install flask
```

Install ReportLab:

```powershell
pip install reportlab
```

Or install both together:

```powershell
pip install flask reportlab
```

---

# 12. Verify Installed Packages

Run:

```powershell
pip list
```

You should see packages including:

```text
Flask
reportlab
```

You can also test Flask:

```powershell
python -c "import flask; print(flask.__version__)"
```

Test ReportLab:

```powershell
python -c "import reportlab; print(reportlab.Version)"
```

---

# 13. SQLite

SQLite does not require a separate installation for this project.

Python already provides SQLite through:

```python
import sqlite3
```

The database file will be:

```text
invoices.db
```

---

# 14. Initialize the Database

After the project files are present, run:

```powershell
python database.py
```

You should see:

```text
Database created successfully!
```

This creates:

```text
invoices.db
```

The database contains two main tables:

```text
invoices
invoice_items
```

---

# 15. Database Structure

## invoices

Stores invoice-level information.

Important columns:

```text
id
invoice_number
customer_name
customer_email
invoice_date
subtotal
gst
grand_total
```

## invoice_items

Stores individual products.

Important columns:

```text
id
invoice_id
product_name
quantity
price
total
```

Relationship:

```text
invoices
   │
   └── invoice_items
```

One invoice can contain multiple invoice items.

---

# 16. Project Structure

The final project structure should look approximately like this:

```text
Invoice-Generator/
│
├── .venv/
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   ├── index.html
│   ├── history.html
│   ├── invoice_details.html
│   └── dashboard.html
│
├── invoices/
│
├── app.py
├── database.py
├── invoice.py
├── login.py
├── signup.py
├── pdf_generator.py
│
├── invoice_counter.txt
├── invoices.db
│
├── .gitignore
└── README.md
```

---

# 17. Important Files

## app.py

Main Flask application.

Responsible for:

* Flask configuration
* Routes
* Invoice generation
* Invoice history
* Invoice details
* PDF downloads
* Invoice deletion
* Dashboard

Run the application using:

```powershell
python app.py
```

---

## database.py

Responsible for:

* Creating the SQLite database
* Creating tables
* Saving invoices
* Saving invoice items
* Retrieving invoices
* Retrieving invoice details
* Deleting invoices
* Dashboard statistics
* Monthly statistics
* Product statistics

---

## pdf_generator.py

Responsible for:

* Generating invoice PDFs
* Generating invoice numbers
* Creating individual PDF files

Generated files are stored in:

```text
invoices/
```

---

## invoice.py

Contains invoice-related functionality from the project structure.

---

## login.py

Reserved for future authentication functionality.

Currently it is not required for the main Invoice Generator workflow.

---

## signup.py

Reserved for future user registration functionality.

Currently it is not required for the main Invoice Generator workflow.

---

# 18. Invoice Number System

Invoice numbers are generated automatically.

The counter is stored in:

```text
invoice_counter.txt
```

Example:

```text
1
```

The application generates:

```text
INV-001
```

Next invoice:

```text
INV-002
```

Next:

```text
INV-003
```

PDF files use the invoice number:

```text
INV-001.pdf
INV-002.pdf
INV-003.pdf
```

---

# 19. Run the Application

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python app.py
```

Flask should display something similar to:

```text
* Running on http://127.0.0.1:5000
```

Open your browser:

```text
http://localhost:5000
```

---

# 20. Main Application URLs

## Home / Create Invoice

```text
http://localhost:5000/
```

## Invoice History

```text
http://localhost:5000/history
```

## Dashboard

```text
http://localhost:5000/dashboard
```

## Invoice Details

Invoice IDs are used in the URL:

```text
http://localhost:5000/invoice/1
```

---

# 21. Creating an Invoice

Open:

```text
http://localhost:5000/
```

Enter:

```text
Customer Name
Customer Email
```

Add products.

Example:

```text
Product: Headset
Quantity: 5
Price: 50000
```

Add another product if required.

Click:

```text
Generate Invoice
```

The application will:

```text
Receive form data
       ↓
Calculate item totals
       ↓
Calculate subtotal
       ↓
Calculate GST
       ↓
Calculate grand total
       ↓
Generate invoice number
       ↓
Generate PDF
       ↓
Save invoice to SQLite
       ↓
Save invoice items to SQLite
       ↓
Return PDF
```

---

# 22. Invoice History

Open:

```text
http://localhost:5000/history
```

The history page displays all saved invoices.

Available operations:

```text
View Details
Delete
```

---

# 23. Downloading an Invoice

Open an invoice's details page.

Click:

```text
Download PDF
```

The application finds the invoice number in the database and downloads the corresponding PDF from:

```text
invoices/
```

---

# 24. Deleting an Invoice

From Invoice History, click:

```text
Delete
```

After confirmation:

```text
Database record
       ↓
Deleted

Invoice items
       ↓
Deleted

PDF file
       ↓
Deleted
```

This keeps the database and generated PDF files synchronized.

---

# 25. Dashboard

Open:

```text
http://localhost:5000/dashboard
```

The dashboard displays:

```text
Total Invoices
Total Revenue
Total GST
Average Invoice
```

It also displays:

```text
Monthly Statistics
Monthly Revenue Chart
Product Sales
Product Revenue Chart
```

---

# 26. Chart.js

The dashboard uses Chart.js through a CDN.

The application does not require Chart.js to be installed using pip.

It is loaded in:

```text
templates/dashboard.html
```

Example:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

An internet connection may therefore be required for the charts to load when using the CDN.

---

# 27. .gitignore

The following files/folders should not be uploaded to GitHub:

```gitignore
# Virtual environment
.venv/

# Python cache
__pycache__/
*.pyc

# SQLite database
invoices.db

# Generated invoice PDFs
invoices/

# Local invoice counter
invoice_counter.txt

# remaining files
login.py
signup.py
```

The following files should remain tracked:

```text
app.py
database.py
pdf_generator.py
static/
templates/
README.md
.gitignore
```

---

# 28. Why the Database Is Ignored

The local database:

```text
invoices.db
```

contains application data generated while using the project.

It should not normally be committed to the GitHub repository.

When another developer clones the project, they can create a fresh database by running:

```powershell
python database.py
```

---

# 29. Why the invoices Folder Is Ignored

The `invoices/` folder contains generated PDF files.

For example:

```text
INV-001.pdf
INV-002.pdf
INV-003.pdf
```

These are generated application data rather than source code.

Therefore they are excluded from Git.

---

# 30. Fresh Installation After Cloning From GitHub

After cloning the repository:

```powershell
git clone <repository-url>
```

Enter the project:

```powershell
cd Invoice-Generator
```

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected:

```text
E:\Invoice-Generator\.venv\Scripts\python.exe
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install flask reportlab
```

Create the database:

```powershell
python database.py
```

Run the application:

```powershell
python app.py
```

Open:

```text
http://localhost:5000
```

---

# 31. Recommended requirements.txt

For easier installation, the project can maintain a `requirements.txt` file.

Create:

```text
requirements.txt
```

Add:

```text
Flask
reportlab
```

Then a new user can install everything with:

```powershell
pip install -r requirements.txt
```

After installing the required packages, run:

```powershell
python database.py
```

and then:

```powershell
python app.py
```

---

# 32. Creating requirements.txt

With the virtual environment activated:

```powershell
pip freeze > requirements.txt
```

This records the installed package versions.

For this project, a minimal requirements file containing the direct dependencies is also acceptable:

```text
Flask
reportlab
```

---

# 33. Troubleshooting

## Flask import error

If VS Code reports:

```text
Import "flask" could not be resolved
```

check the selected interpreter.

Use:

```text
Ctrl + Shift + P
```

Then:

```text
Python: Select Interpreter
```

Select:

```text
E:\Invoice-Generator\.venv\Scripts\python.exe
```

---

## ReportLab import error

Make sure the virtual environment is activated:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```powershell
pip install reportlab
```

---

## Flask does not start

Check:

```powershell
python app.py
```

If necessary, verify:

```powershell
python --version
pip list
```

---

## Database does not exist

Run:

```powershell
python database.py
```

This creates:

```text
invoices.db
```

---

## PowerShell cannot activate .venv

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Port 5000 is already being used

Stop the previous Flask process or close the terminal where Flask is running.

Then restart:

```powershell
python app.py
```

---

# 34. Development Workflow

Every time you work on the project:

```powershell
cd E:\Invoice-Generator
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the application:

```powershell
python app.py
```

Open:

```text
http://localhost:5000
```

When finished:

```text
CTRL + C
```

to stop Flask.

---

# 35. Testing Checklist

The project has been tested through the complete workflow.

```text
Create Invoice              ✅
Multiple Products           ✅
GST Calculation             ✅
PDF Generation              ✅
PDF Storage                 ✅
Database Storage            ✅
Invoice History             ✅
Invoice Details             ✅
PDF Download                ✅
Invoice Deletion            ✅
Dashboard Statistics        ✅
Monthly Statistics          ✅
Monthly Revenue Chart       ✅
Product Statistics          ✅
Product Revenue Chart       ✅
```

---

# 36. Data Flow

The application follows this general architecture:

```text
                 Browser
                    │
                    ▼
              Flask Application
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      SQLite DB           PDF Generator
          │                   │
          ▼                   ▼
   Invoice Records       PDF Files
          │
          ▼
       Dashboard
          │
          ▼
      Analytics
```

---

# 37. Future Improvements

The current project is Version 1.0.

Possible future improvements include:

* User authentication
* Signup/Login
* Password hashing
* Multiple users
* Customer management
* Product management
* Invoice search
* Invoice filtering
* Date-range filtering
* Invoice editing
* Email invoice functionality
* Company information
* Company logo
* More GST options
* Export to CSV
* Export to Excel
* REST API
* PostgreSQL
* Cloud deployment
* Automated backups

---

# 38. Data Engineering Extension

The current application can also be extended into a Data Engineering project.

Possible architecture:

```text
Invoice Application
        ↓
SQLite
        ↓
Extract
        ↓
Transform
        ↓
Data Cleaning
        ↓
PostgreSQL / Azure SQL
        ↓
Data Warehouse
        ↓
Power BI
        ↓
Business Analytics
```

Possible ETL tasks:

```text
Extract invoice data
        ↓
Clean customer/product data
        ↓
Transform dates and monetary values
        ↓
Aggregate sales
        ↓
Load into PostgreSQL
        ↓
Create analytical reports
```

This can make the project more relevant to a Data Engineering portfolio.

---

# 39. Project Status

**Version:** 1.0

**Status:** Completed

The current Version 1.0 includes:

```text
Invoice Creation
PDF Generation
SQLite Storage
Invoice History
Invoice Details
PDF Download
Invoice Deletion
Dashboard
Revenue Analytics
Product Analytics
```

Future features should be developed as separate versions rather than modifying the stable Version 1.0 unnecessarily.

---

# 40. Quick Start

For an already configured project:

```powershell
cd E:\Invoice-Generator
```

Activate environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run application:

```powershell
python app.py
```

Open:

```text
http://localhost:5000
```

For a fresh setup:

```powershell
cd E:\Invoice-Generator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install flask reportlab
python database.py
python app.py
```

Then open:

```text
http://localhost:5000
```

---

# 41. Author

**Shaikh Arsalan**

Project: **Invoice Generator**

Technologies:

```text
Python
Flask
SQLite
SQL
ReportLab
HTML
CSS
JavaScript
Chart.js
```

This project was developed as a practical Python web application and can serve as a foundation for future Data Engineering and analytics work.
<<<<<<< HEAD
=======

>>>>>>> f503c51fc46ec35069d7b9319e240446eecf77f9
