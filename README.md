# Invoice Generator

A full-stack invoice management web application built with **Python, Flask, PostgreSQL, ReportLab, Cloudinary, and Resend**.

The application allows users to create professional invoices, generate PDF documents, manage invoice history, securely store generated PDFs in the cloud, and manage their accounts. It also includes a role-based admin system with user, invoice, revenue, and activity monitoring.

The project was initially developed as a local Flask + SQLite application and was later migrated to **PostgreSQL** and deployed publicly on **Render** with **Cloudinary** for PDF storage and **Resend** for password-reset emails.

---

## Live Application

**Invoice Generator:**
https://invoice-generator-96ez.onrender.com

The application is publicly deployed using Render.

---

# 1. Project Overview

The Invoice Generator project was created to learn and implement practical concepts in:

* Python
* Flask
* HTML
* CSS
* JavaScript
* SQL
* PostgreSQL
* Authentication
* Database design
* PDF generation
* Cloud storage
* REST-style application routes
* Email APIs
* Role-based access control
* Dashboard analytics
* Git and GitHub
* Cloud deployment
* Application debugging
* Production testing

The project evolved from a simple invoice-generation application into a multi-user cloud-based web application.

---

# 2. Main Features

## User Features

* User registration
* User login
* User logout
* Session-based authentication
* User profile
* Change password
* Delete account
* Forgot password
* Password reset
* Anti-account-enumeration response for password reset
* User-specific invoice data
* User-specific invoice numbering

## Invoice Features

* Create invoices
* Add multiple products
* Enter product quantities
* Enter product prices
* Automatic subtotal calculation
* Automatic GST calculation
* Automatic grand-total calculation
* Generate PDF invoices
* Invoice history
* Invoice details
* Download invoices
* Soft delete invoices
* Trash system
* Restore deleted invoices
* Permanently delete invoices
* Cloudinary PDF storage

## Dashboard Features

* Total invoice count
* Total revenue
* Total GST
* Average invoice value
* Invoice analytics
* Chart.js visualizations
* User-specific dashboard data

## Admin Features

* Admin role
* Admin dashboard
* Total users
* Total invoices
* Revenue information
* User management
* Invoice management
* Activity logs
* Invoice detail viewing
* Protected admin routes

## Deployment Features

* PostgreSQL production database
* Cloudinary authenticated storage
* Resend email API
* Gunicorn production server
* Render deployment
* Environment-variable based secrets
* Automatic GitHub-to-Render deployment

---

# 3. Technology Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Application logic             |
| Flask      | Web framework                 |
| HTML       | Page structure                |
| CSS        | Styling and responsive design |
| JavaScript | Client-side interaction       |
| PostgreSQL | Production database           |
| ReportLab  | PDF generation                |
| Cloudinary | Cloud PDF storage             |
| Resend     | Password-reset email delivery |
| Chart.js   | Dashboard charts              |
| Gunicorn   | Production WSGI server        |
| Render     | Cloud deployment              |
| Git        | Version control               |
| GitHub     | Source-code hosting           |

---

# 4. Current Production Architecture

```text
                         USER
                          │
                          ▼
                    WEB BROWSER
                          │
                          ▼
                  FLASK APPLICATION
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
        PostgreSQL    Cloudinary     Resend
         Database     PDF Storage     Email
             │
             ▼
       Dashboard / Admin
             │
             ▼
          Analytics
```

### PostgreSQL

Stores application data such as:

* Users
* Roles
* Invoices
* Invoice items
* Invoice counters
* Password-reset tokens
* Activity logs

### Cloudinary

Stores generated invoice PDFs using authenticated raw assets.

### Resend

Handles password-reset email delivery.

### Render

Hosts the Flask application and production PostgreSQL database.

---

# 5. Invoice Workflow

The main invoice workflow is:

```text
User Login
    ↓
Create Invoice
    ↓
Enter Customer Information
    ↓
Add Products
    ↓
Calculate Subtotal
    ↓
Calculate GST
    ↓
Calculate Grand Total
    ↓
Generate PDF
    ↓
Upload PDF to Cloudinary
    ↓
Save Invoice Metadata in PostgreSQL
    ↓
Display Invoice Details
    ↓
Invoice History
    ↓
Download PDF
```

---

# 6. Invoice Calculation

The application currently uses an **18% GST rate**.

### Subtotal

```text
Subtotal = Σ (Quantity × Price)
```

### GST

```text
GST = Subtotal × 18 / 100
```

### Grand Total

```text
Grand Total = Subtotal + GST
```

For example:

```text
Product 1 = ₹500
Product 2 = ₹300

Subtotal = ₹800

GST = ₹800 × 18 / 100
    = ₹144

Grand Total = ₹944
```

---

# 7. User-Specific Invoice Numbering

Invoice numbers are maintained separately for each user.

The application uses the `invoice_counters` table to maintain invoice numbering.

This prevents one user's invoice numbering system from interfering with another user's invoices.

The database also enforces:

```text
UNIQUE(user_id, invoice_number)
```

Therefore, the same invoice number can exist for different users but cannot be duplicated for the same user.

---

# 8. User Data Isolation

Each invoice belongs to a specific user through:

```text
user_id
```

Database queries use the logged-in user's ID when retrieving or modifying invoices.

For example:

```sql
WHERE id = %s
AND user_id = %s
```

This prevents one user from accessing another user's invoices through normal application routes.

---

# 9. PDF Generation

Invoice PDFs are generated using **ReportLab**.

The application temporarily creates the PDF in the local `invoices/` directory.

Example staging filename:

```text
user_3_INV-001.pdf
```

The local directory is only used as temporary PDF staging.

It is not the permanent production storage location.

---

# 10. Cloudinary PDF Storage

After generating a PDF:

```text
Generate PDF
      ↓
Temporary local PDF
      ↓
Upload to Cloudinary
      ↓
Save Cloudinary public ID
      ↓
PDF available through authenticated cloud storage
```

Cloudinary is configured for:

```text
resource_type = raw
type = authenticated
```

The application's database stores the Cloudinary identifier in:

```text
pdf_public_id
```

The application uses signed Cloudinary URLs when downloading protected PDFs.

---

# 11. Invoice Deletion System

Invoices use a soft-delete system.

The `invoices` table contains:

```text
deleted
deleted_at
```

## Delete

When a user deletes an invoice:

```text
Invoice
   ↓
deleted = 1
   ↓
Invoice moves to Trash
```

The invoice is not immediately removed from the database.

## Restore

A deleted invoice can be restored:

```text
Trash
   ↓
Restore
   ↓
deleted = 0
```

## Permanent Delete

Permanent deletion removes:

1. Invoice items
2. Invoice database record
3. Cloudinary PDF

The application also logs the permanent deletion activity.

---

# 12. Database Structure

The current PostgreSQL database contains the following main tables:

```text
users
│
├── invoices
│     │
│     └── invoice_items
│
├── invoice_counters
│
├── password_reset_tokens
│
└── activity_logs
```

## users

Stores user information and role information.

Important fields include:

```text
id
name
email
password
role
```

Roles currently include:

```text
user
admin
```

## invoices

Stores invoice-level information.

Important fields include:

```text
id
user_id
invoice_number
customer_name
customer_email
invoice_date
subtotal
gst
grand_total
deleted
deleted_at
pdf_public_id
```

## invoice_items

Stores individual products belonging to invoices.

Important fields include:

```text
invoice_id
product_name
quantity
price
total
```

## invoice_counters

Maintains invoice numbering for individual users.

## password_reset_tokens

Stores temporary password-reset tokens and their expiration information.

## activity_logs

Stores application activity such as:

```text
Login
Logout
Invoice creation
Invoice deletion
Invoice restoration
Permanent invoice deletion
Account deletion
Other administrative/user activities
```

---

# 13. Authentication System

The application includes a complete authentication workflow.

```text
Signup
  ↓
Login
  ↓
Authenticated Session
  ↓
Dashboard
```

Protected invoice routes require:

```python
session["user_id"]
```

Users cannot access protected invoice functionality without authentication.

---

# 14. Password Management

Users can:

* Change their password
* Request a password reset
* Reset their password using a temporary token
* Delete their account

The password-reset system uses an expiring token.

The application does not reveal whether an email address exists in the database when processing a forgot-password request.

This helps prevent account enumeration.

---

# 15. Password Reset Email System

The project originally experimented with Gmail SMTP.

Gmail SMTP was later removed from the production architecture because the deployment environment did not provide the required SMTP connectivity.

The application now uses the **Resend API**.

Current flow:

```text
Forgot Password
      ↓
Enter Email
      ↓
Generate Reset Token
      ↓
Store Token in PostgreSQL
      ↓
Send Email through Resend
      ↓
User Opens Reset Link
      ↓
Set New Password
```

The project currently uses:

```text
onboarding@resend.dev
```

for the Resend testing configuration.

With Resend's testing sender, email delivery is restricted to the appropriate Resend testing recipient rules.

For unrestricted production email delivery, a verified domain and sender should be configured in Resend.

---

# 16. Admin System

Users have a `role` field.

Example:

```text
role = user
role = admin
```

Admin-only routes check the authenticated user's role before providing access.

The admin system includes:

* Admin dashboard
* User list
* Invoice list
* Activity logs
* Revenue information
* Invoice information
* User information

The admin invoice detail page is intentionally view-oriented and does not provide normal user invoice-management controls.

---

# 17. Dashboard Analytics

The user dashboard provides information such as:

```text
Total Invoices
Revenue
GST
Average Invoice Value
```

Charts are rendered using:

```text
Chart.js
```

The dashboard data is retrieved from the PostgreSQL database.

---

# 18. Account Deletion

Users can permanently delete their accounts.

The account deletion process removes associated database records such as:

```text
Invoice items
Invoices
Password-reset tokens
Invoice counters
Activity logs
User account
```

The deletion process is performed using database transactions.

The old local-PDF cleanup logic was removed because production invoice PDFs are managed through Cloudinary.

---

# 19. Security Measures

The application includes several security-related measures:

* Environment variables for secrets
* `.env` excluded from Git
* Session-based authentication
* User-specific database queries
* Role-based admin protection
* Expiring password-reset tokens
* Generic forgot-password response
* Protected Cloudinary PDFs
* Signed Cloudinary download URLs
* Security headers
* Database transactions
* User-specific invoice numbering

Secrets must never be committed to GitHub.

---

# 20. Environment Variables

The application uses environment variables for configuration.

Create a local `.env` file:

```env
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

RESEND_API_KEY=your_resend_api_key
```

Never commit the `.env` file.

---

# 21. `.gitignore`

The current `.gitignore` contains:

```gitignore
# Virtual environment
.venv/

# Python cache
__pycache__/
*.pyc

# Database
*.db

# Generated invoice PDFs
invoices/

.env
```

The `invoices/` directory is ignored because generated PDFs are temporary local files and should not be committed.

---

# 22. Requirements

The current production dependency versions are:

```text
psycopg2-binary==2.9.13
psycopg2-pool==1.2
blinker==1.9.0
charset-normalizer==3.5.1
click==8.5.0
Flask==3.1.3
gunicorn==26.2.0
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
pillow==12.3.0
python-dotenv==1.2.3
reportlab==5.0.1
Werkzeug==3.1.8
cloudinary==1.46.2
resend==2.47.0
```

---

# 23. Prerequisites

To develop this project locally, install:

* Python
* PostgreSQL
* Git
* VS Code (recommended)
* A Cloudinary account
* A Resend account

For deployment:

* GitHub account
* Render account
* PostgreSQL database
* Cloudinary account
* Resend account

---

# 24. Create the Project

Create the project directory:

```powershell
mkdir E:\Invoice-Generator
cd E:\Invoice-Generator
```

---

# 25. Create the Virtual Environment

Create a Python virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

The terminal should then display:

```text
(.venv)
```

---

# 26. Verify Python

Run:

```powershell
python --version
```

The project was developed using Python 3.14.x locally.

---

# 27. Install Dependencies

Install the requirements:

```powershell
pip install -r requirements.txt
```

For a new project, the dependency list can also be installed individually before generating `requirements.txt`.

---

# 28. PostgreSQL Local Setup

The production application uses PostgreSQL.

For local development, PostgreSQL should be available from the local machine or another externally accessible PostgreSQL server.

A typical local connection string looks like:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/invoice_generator
```

The database name can be created through:

* PostgreSQL `psql`
* pgAdmin
* Another PostgreSQL administration tool

The current application is designed around PostgreSQL and should not be configured to use the old SQLite database.

---

# 29. Important Local Database Note

The Render PostgreSQL database uses an internal Render hostname for the deployed service.

That internal hostname is not intended to be used directly from a local Windows machine.

Therefore, local development should use:

```text
Local PostgreSQL
```

or another PostgreSQL server that is externally accessible.

Production uses the PostgreSQL database configured through Render.

---

# 30. Database Initialization

The Flask application initializes the required PostgreSQL database structure when the application starts.

The database logic is contained in:

```text
database.py
```

This module contains the database connection, initialization, queries, invoice operations, user operations, admin operations, and related database functionality.

---

# 31. Project Structure

The project is organized approximately as follows:

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
│   ├── dashboard.html
│   ├── history.html
│   ├── invoice_details.html
│   ├── login.html
│   ├── signup.html
│   ├── ...
│   └── admin / profile / password-reset / trash templates
│
├── app.py
├── database.py
├── pdf_generator.py
├── forgot_password.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

The `.env` file exists only in the local environment and is intentionally ignored by Git.

The `invoices/` directory is created automatically when invoice PDFs are generated.

---

# 32. Main Python Modules

## app.py

The main Flask application.

Responsible for:

* Flask configuration
* Routes
* Sessions
* Authentication flow
* Invoice routes
* Dashboard
* Admin routes
* Profile functionality
* Account deletion
* Cloudinary operations
* Password-reset handling

## database.py

Responsible for:

* PostgreSQL connection
* Database initialization
* Users
* Invoices
* Invoice items
* Invoice counters
* Password-reset tokens
* Activity logs
* Admin database operations

## pdf_generator.py

Responsible for:

* Invoice PDF creation
* Invoice formatting
* Customer information
* Product information
* GST
* Totals
* Temporary PDF generation

## forgot_password.py

Responsible for:

* Password-reset email functionality
* Resend API integration

---

# 33. Running the Application Locally

After configuring a valid local PostgreSQL database and `.env` file:

```powershell
python app.py
```

The Flask development server runs on:

```text
http://127.0.0.1:5000
```

Open the address in a browser.

---

# 34. Local Syntax Testing

Before running the application, Python files can be checked for syntax errors:

```powershell
python -m py_compile app.py database.py pdf_generator.py
```

If the command produces no output, the files passed the Python syntax check.

---

# 35. Local Testing Checklist

A complete local test should include:

### Authentication

* [ ] Signup
* [ ] Login
* [ ] Logout
* [ ] Invalid login
* [ ] Protected route access
* [ ] Profile
* [ ] Change password
* [ ] Delete account

### Password Reset

* [ ] Existing email
* [ ] Non-existing email
* [ ] Reset link
* [ ] Expired token
* [ ] New password

### Invoice

* [ ] Create invoice
* [ ] Add one product
* [ ] Add multiple products
* [ ] Verify subtotal
* [ ] Verify GST
* [ ] Verify grand total
* [ ] Generate PDF
* [ ] Upload PDF
* [ ] Open invoice details
* [ ] Download PDF

### Invoice Management

* [ ] Invoice history
* [ ] Delete invoice
* [ ] Open trash
* [ ] Restore invoice
* [ ] Permanently delete invoice
* [ ] Verify Cloudinary deletion

### User Isolation

* [ ] Create invoices with User A
* [ ] Login as User B
* [ ] Verify User B cannot see User A's invoices

### Admin

* [ ] Admin login
* [ ] Admin dashboard
* [ ] User list
* [ ] Invoice list
* [ ] Activity logs
* [ ] Invoice details
* [ ] Verify normal user cannot access admin routes

### UI

* [ ] Desktop
* [ ] Mobile
* [ ] Dashboard
* [ ] Forms
* [ ] Navigation
* [ ] Invoice history
* [ ] Admin pages

---

# 36. Git Repository

The source code is maintained in Git.

Repository:

```text
Arsalan-Dev-Cloud/Invoice-Generator
```

Typical workflow:

```powershell
git status
git add .
git commit -m "Your commit message"
git push origin main
```

---

# 37. GitHub Deployment Workflow

The project is connected to Render through GitHub.

The general deployment workflow is:

```text
Local Changes
     ↓
Git Commit
     ↓
Git Push
     ↓
GitHub
     ↓
Render detects new commit
     ↓
Build
     ↓
Deploy
     ↓
Live Application
```

---

# 38. Render Configuration

The production application is deployed on Render.

Current deployment configuration:

```text
Service Type: Web Service
Runtime: Python
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

Gunicorn is used by Render for the production Flask application.

---

# 39. Why Gunicorn Is Not Used for Windows Local Development

The production start command is:

```powershell
gunicorn app:app
```

Gunicorn is primarily designed for Unix-like production environments.

When attempting to run it directly on Windows, errors involving:

```text
fcntl
```

can occur.

For local Windows development, use:

```powershell
python app.py
```

For Render production, use:

```text
gunicorn app:app
```

---

# 40. Render Environment Variables

The following environment variables are configured in Render:

```text
DATABASE_URL
SECRET_KEY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
RESEND_API_KEY
```

Secret values must be entered through Render's environment-variable configuration.

They must never be committed to GitHub.

---

# 41. Render PostgreSQL

The production application uses a PostgreSQL database provisioned through Render.

The web service receives the database connection through:

```text
DATABASE_URL
```

The application therefore does not require hard-coded database credentials.

---

# 42. Cloudinary Configuration

Cloudinary is used for permanent invoice PDF storage.

Required variables:

```env
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

The API secret must remain private.

The PDFs are uploaded as authenticated raw assets.

---

# 43. Resend Configuration

Resend is used for password-reset emails.

Required variable:

```env
RESEND_API_KEY=
```

The application handles email-delivery errors so that a failed reset-email attempt does not unnecessarily result in an application 500 error.

For full production email delivery to arbitrary users, configure and verify a domain in Resend and use a verified sender address.

---

# 44. Production Testing

After deployment, the following production tests were performed:

```text
Login
    ↓
Dashboard
    ↓
Create Invoice
    ↓
Invoice Details
    ↓
Invoice History
    ↓
Cloudinary PDF Download
    ↓
Soft Delete
    ↓
Trash
    ↓
Permanent Delete
    ↓
Cloudinary PDF Cleanup
```

The production application successfully handled these workflows.

Additional production testing included:

* Authentication
* User isolation
* Admin dashboard
* Admin users
* Admin activity
* Admin invoices
* Password change
* Account deletion
* Forgot-password anti-enumeration behavior
* Mobile responsiveness
* Cloudinary authenticated downloads

---

# 45. Error Handling

The application was tested against several failure cases.

Examples include:

* Invalid login
* Unauthorized routes
* Invalid password
* Non-existent password-reset email
* Password-reset email delivery failure
* Invalid invoice access
* Unauthorized admin access
* Database errors
* Cloudinary errors

Production errors should be investigated using Render logs.

---

# 46. Troubleshooting

## Flask does not start

Check:

```powershell
python --version
```

Check the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then:

```powershell
python app.py
```

---

## Database connection fails

Check:

```env
DATABASE_URL
```

Make sure the PostgreSQL server is running and the database credentials are correct.

For local development, do not use a Render-internal hostname that is inaccessible from the local machine.

---

## Render application returns 500

Open the Render service logs.

Look for:

```text
Traceback
Exception
Database error
Cloudinary error
```

The production logs are the primary source for diagnosing deployment errors.

---

## Password reset email does not arrive

Check:

```text
RESEND_API_KEY
```

Also verify the Resend sender and recipient restrictions.

The current testing sender:

```text
onboarding@resend.dev
```

has testing limitations.

---

## Cloudinary download fails

Check:

```text
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

Also verify that the PDF was uploaded as an authenticated raw asset and that the database contains the correct:

```text
pdf_public_id
```

---

# 47. Migration History

The project originally used SQLite during early development.

The architecture was later migrated to PostgreSQL for the production application.

The original architecture was approximately:

```text
Flask
  ↓
SQLite
  ↓
Local PDF Files
```

The current architecture is:

```text
Flask
  ↓
PostgreSQL
  ├── User Data
  ├── Invoice Data
  ├── Activity Data
  └── Authentication Data

PDF
  ↓
Cloudinary

Password Reset
  ↓
Resend
```

Old SQLite database files were archived outside the active project directory and are not part of the current production application.

---

# 48. Temporary PDF Storage

Although production PDFs are stored in Cloudinary, the application temporarily creates PDFs locally before uploading them.

The workflow is:

```text
ReportLab
   ↓
Temporary invoices/ file
   ↓
Cloudinary upload
   ↓
Cloudinary permanent storage
```

The `invoices/` directory is therefore ignored by Git.

It should not be interpreted as the production PDF database.

---

# 49. Security and Secrets

Never commit:

```text
.env
```

Never publish:

```text
CLOUDINARY_API_SECRET
RESEND_API_KEY
SECRET_KEY
DATABASE_URL
```

If a secret is accidentally exposed, revoke or rotate it immediately through the corresponding service.

---

# 50. Data Engineering Relevance

Although this project is primarily a web application, it is also useful as a practical Data Engineering learning project.

It demonstrates:

### Relational Database Design

The project uses normalized relational tables:

```text
users
invoices
invoice_items
invoice_counters
password_reset_tokens
activity_logs
```

### SQL

The application performs:

* SELECT
* INSERT
* UPDATE
* DELETE
* JOIN-like relational operations
* Filtering
* Aggregation
* Transaction management

### Data Relationships

Examples:

```text
User
 ↓
Invoices
 ↓
Invoice Items
```

### Analytics

The dashboard calculates:

* Invoice counts
* Revenue
* GST
* Average invoice values

### Cloud Architecture

The project uses:

```text
Application → Render
Database → PostgreSQL
Files → Cloudinary
Email → Resend
Source Code → GitHub
```

This gives practical exposure to cloud-based application architecture.

---

# 51. Possible Data Engineering Extensions

Future versions could extend the project into a stronger Data Engineering portfolio project by adding:

* ETL pipelines
* Scheduled data extraction
* PostgreSQL → data warehouse pipelines
* Apache Spark
* Azure Data Factory
* Azure Blob Storage
* Azure SQL
* Databricks
* Power BI
* Data quality checks
* Historical sales analysis
* Customer analytics
* Revenue forecasting
* Monthly reporting pipelines

These are potential future extensions and are not currently part of the production application.

---

# 52. Possible Future Improvements

Potential application improvements include:

* Custom domain
* Production email domain
* More advanced invoice templates
* Company branding
* Invoice logo upload
* Multiple GST rates
* Tax configuration
* Recurring invoices
* Invoice search and filtering
* CSV/Excel export
* Advanced admin analytics
* Automated backups
* Automated database migrations
* API endpoints
* Rate limiting
* More advanced audit logging
* Automated testing
* CI/CD
* Docker deployment

---

# 53. Current Project Status

The current application is a publicly deployed multi-user invoice management system.

Implemented production functionality includes:

```text
✓ Flask application
✓ PostgreSQL database
✓ User authentication
✓ User isolation
✓ Admin role
✓ Invoice creation
✓ Invoice numbering
✓ GST calculation
✓ PDF generation
✓ Cloudinary storage
✓ Invoice history
✓ Invoice details
✓ PDF download
✓ Soft delete
✓ Trash
✓ Restore
✓ Permanent deletion
✓ Cloudinary PDF cleanup
✓ Dashboard analytics
✓ Admin dashboard
✓ Activity logging
✓ Password change
✓ Password reset
✓ Resend integration
✓ Account deletion
✓ Responsive UI
✓ GitHub repository
✓ Render deployment
✓ Production testing
```

---

# 54. Quick Start

For a new development environment:

```powershell
git clone <repository-url>

cd Invoice-Generator

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Configure:

```text
.env
PostgreSQL
Cloudinary
Resend
```

Then run:

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

# 55. Useful Development Commands

Activate environment:

```powershell
.venv\Scripts\Activate.ps1
```

Run Flask:

```powershell
python app.py
```

Check Python syntax:

```powershell
python -m py_compile app.py database.py pdf_generator.py
```

Check Git:

```powershell
git status
```

Search the project:

```powershell
git grep -n "search-term"
```

Commit changes:

```powershell
git add .
git commit -m "Your commit message"
```

Push changes:

```powershell
git push origin main
```

---

# 56. Development Philosophy

This project was developed incrementally.

The development process involved:

```text
Idea
 ↓
Basic Flask Application
 ↓
Invoice Generation
 ↓
PDF Generation
 ↓
Database Integration
 ↓
Authentication
 ↓
Multi-user Data Isolation
 ↓
Admin System
 ↓
Dashboard
 ↓
PostgreSQL Migration
 ↓
Cloudinary Storage
 ↓
Resend Email
 ↓
Production Deployment
 ↓
Production Testing
 ↓
Cleanup and Documentation
```

The project therefore represents not only the final application but also the practical development process of turning a local Python application into a deployed cloud application.

---

# 57. Author

**Shaikh Arsalan**

GitHub:

```text
Arsalan-Dev-Cloud
```

---

# 58. Final Notes

This project is intended as both:

1. A functional invoice management application
2. A practical learning project covering Python, Web Development, SQL, databases, cloud services, authentication, deployment, and foundational Data Engineering concepts

The production architecture is based on:

```text
Python
+
Flask
+
PostgreSQL
+
ReportLab
+
Cloudinary
+
Resend
+
Chart.js
+
Render
+
GitHub
```

The application has progressed from its original local SQLite implementation into a publicly deployed multi-user cloud application.
