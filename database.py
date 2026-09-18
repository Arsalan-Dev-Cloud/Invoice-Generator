import sqlite3
import os


DATABASE_NAME = "invoices.db"


def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

        # Invoice table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            invoice_number TEXT UNIQUE,

            customer_name TEXT NOT NULL,

            customer_email TEXT NOT NULL,

            invoice_date TEXT NOT NULL,

            subtotal REAL NOT NULL,

            gst REAL NOT NULL,

            grand_total REAL NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)

        )
    """)

    # Invoice items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            invoice_id INTEGER,

            product_name TEXT NOT NULL,

            quantity INTEGER NOT NULL,

            price REAL NOT NULL,

            total REAL NOT NULL,

            FOREIGN KEY (invoice_id)
                REFERENCES invoices(id)

        )
    """)

        # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    # Add role column to existing users table if it does not exist

    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]

    if "role" not in user_columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT DEFAULT 'user'
        """)

        # Password reset tokens table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

        # Add user_id column to existing invoices table
    cursor.execute("""
        PRAGMA table_info(invoices)
    """)

    columns = cursor.fetchall()

    column_names = [column[1] for column in columns]

    if "user_id" not in column_names:

        cursor.execute("""
            ALTER TABLE invoices
            ADD COLUMN user_id INTEGER
        """)

    connection.commit()

    connection.close()

def save_invoice(
    user_id,
    invoice_number,
    customer_name,
    customer_email,
    invoice_date,
    subtotal,
    gst,
    grand_total,
    product_names,
    quantities,
    prices
):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    # Save invoice information
    cursor.execute("""
        INSERT INTO invoices (
            user_id,
            invoice_number,
            customer_name,
            customer_email,
            invoice_date,
            subtotal,
            gst,
            grand_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        invoice_number,
        customer_name,
        customer_email,
        invoice_date,
        subtotal,
        gst,
        grand_total
    ))

    # Get the ID of the newly created invoice
    invoice_id = cursor.lastrowid

    # Save each invoice item
    for i in range(len(product_names)):

        product_name = product_names[i]
        quantity = int(quantities[i])
        price = float(prices[i])

        total = quantity * price

        cursor.execute("""
            INSERT INTO invoice_items (
                invoice_id,
                product_name,
                quantity,
                price,
                total
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            invoice_id,
            product_name,
            quantity,
            price,
            total
        ))

    connection.commit()

    connection.close()

    print("Invoice saved to database!")

def get_all_invoices(user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            invoice_number,
            customer_name,
            customer_email,
            invoice_date,
            subtotal,
            gst,
            grand_total
        FROM invoices
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    invoices = cursor.fetchall()

    connection.close()

    return invoices

def get_invoice_details(invoice_id, user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get invoice information
    cursor.execute("""
        SELECT *
        FROM invoices
        WHERE id = ?
        AND user_id = ?
    """, (invoice_id, user_id))

    invoice = cursor.fetchone()

    # If invoice does not belong to this user
    if invoice is None:
        connection.close()
        return None, []

    # Get items belonging to this invoice
    cursor.execute("""
        SELECT *
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,))

    items = cursor.fetchall()

    connection.close()

    return invoice, items

def delete_invoice(invoice_id, user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    # Delete invoice items only if invoice belongs to this user
    cursor.execute("""
        DELETE FROM invoice_items
        WHERE invoice_id = ?
        AND invoice_id IN (
            SELECT id
            FROM invoices
            WHERE id = ?
            AND user_id = ?
        )
    """, (
        invoice_id,
        invoice_id,
        user_id
    ))

    # Delete invoice only if it belongs to this user
    cursor.execute("""
        DELETE FROM invoices
        WHERE id = ?
        AND user_id = ?
    """, (
        invoice_id,
        user_id
    ))

    connection.commit()

    connection.close()

    print("Invoice deleted successfully!")

def get_invoice_statistics(user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(grand_total), 0),
            COALESCE(SUM(gst), 0),
            COALESCE(AVG(grand_total), 0)
        FROM invoices
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    return {
        "total_invoices": result[0],
        "total_revenue": result[1],
        "total_gst": result[2],
        "average_invoice": result[3]
    }

def get_monthly_statistics(user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            substr(invoice_date, 4, 7) AS month,
            COUNT(*) AS invoice_count,
            SUM(grand_total) AS revenue
        FROM invoices
        WHERE user_id = ?
        GROUP BY substr(invoice_date, 4, 7)
        ORDER BY substr(invoice_date, 7, 4),
                 substr(invoice_date, 4, 2)
    """, (user_id,))

    results = cursor.fetchall()

    connection.close()

    return results

def get_product_statistics(user_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            invoice_items.product_name,
            SUM(invoice_items.quantity) AS total_quantity,
            SUM(invoice_items.total) AS total_revenue
        FROM invoice_items
        INNER JOIN invoices
            ON invoice_items.invoice_id = invoices.id
        WHERE invoices.user_id = ?
        GROUP BY invoice_items.product_name
        ORDER BY total_quantity DESC
    """, (user_id,))

    results = cursor.fetchall()

    connection.close()

    return results

def create_user(name, email, password):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
    """, (
        name,
        email,
        password
    ))

    connection.commit()

    connection.close()

def get_user_by_email(email):

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user

def create_password_reset_token(user_id, token, expires_at):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO password_reset_tokens (
            user_id,
            token,
            expires_at
        )
        VALUES (?, ?, ?)
    """, (
        user_id,
        token,
        expires_at
    ))

    connection.commit()
    connection.close()


def get_password_reset_token(token):
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM password_reset_tokens
        WHERE token = ?
    """, (token,))

    reset_token = cursor.fetchone()

    connection.close()

    return reset_token


def mark_reset_token_used(token):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE password_reset_tokens
        SET used = 1
        WHERE token = ?
    """, (token,))

    connection.commit()
    connection.close()


def update_user_password(user_id, hashed_password):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET password = ?
        WHERE id = ?
    """, (
        hashed_password,
        user_id
    ))

    connection.commit()
    connection.close()

def get_total_users():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    total_users = cursor.fetchone()[0]

    connection.close()

    return total_users


def get_total_invoices():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM invoices
    """)

    total_invoices = cursor.fetchone()[0]

    connection.close()

    return total_invoices


def get_total_revenue():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM invoices
    """)

    total_revenue = cursor.fetchone()[0]

    connection.close()

    return total_revenue

def get_all_users():

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            users.id,
            users.name,
            users.email,
            users.role,
            COUNT(invoices.id) AS invoice_count
        FROM users
        LEFT JOIN invoices
            ON users.id = invoices.user_id
        GROUP BY
            users.id,
            users.name,
            users.email,
            users.role
        ORDER BY users.id
    """)

    users = cursor.fetchall()

    connection.close()

    return users


def get_all_invoices_admin():

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            invoices.id,
            invoices.invoice_number,
            invoices.customer_name,
            invoices.customer_email,
            invoices.invoice_date,
            invoices.grand_total,
            users.name AS user_name,
            users.email AS user_email
        FROM invoices
        LEFT JOIN users
            ON invoices.user_id = users.id
        ORDER BY invoices.id DESC
    """)

    invoices = cursor.fetchall()

    connection.close()

    return invoices

def get_recent_invoices(limit=5):

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            invoices.invoice_number,
            invoices.customer_name,
            invoices.invoice_date,
            invoices.grand_total,
            users.name AS user_name
        FROM invoices
        LEFT JOIN users
            ON invoices.user_id = users.id
        ORDER BY invoices.id DESC
        LIMIT ?
    """, (limit,))

    invoices = cursor.fetchall()

    connection.close()

    return invoices

def delete_user_account(user_id):

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get invoice numbers before deleting invoices
    cursor.execute("""
        SELECT invoice_number
        FROM invoices
        WHERE user_id = ?
    """, (user_id,))

    invoices = cursor.fetchall()

    # Delete invoice items
    cursor.execute("""
        DELETE FROM invoice_items
        WHERE invoice_id IN (
            SELECT id
            FROM invoices
            WHERE user_id = ?
        )
    """, (user_id,))

    # Delete invoices
    cursor.execute("""
        DELETE FROM invoices
        WHERE user_id = ?
    """, (user_id,))

    # Delete password reset tokens
    cursor.execute("""
        DELETE FROM password_reset_tokens
        WHERE user_id = ?
    """, (user_id,))

    # Delete user account
    cursor.execute("""
        DELETE FROM users
        WHERE id = ?
    """, (user_id,))

    connection.commit()
    connection.close()

    # Delete generated invoice PDF files
    for invoice in invoices:

        invoice_number = invoice["invoice_number"]

        file_path = os.path.join(
            "invoices",
            f"{invoice_number}.pdf"
        )

        if os.path.exists(file_path):
            os.remove(file_path)

    print("User account and associated data deleted successfully!")


def update_user_name(user_id, new_name):

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?
        WHERE id = ?
    """, (new_name, user_id))

    connection.commit()
    connection.close()

    print("User name updated successfully!")


def get_admin_count():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role = 'admin'
    """)

    admin_count = cursor.fetchone()[0]

    connection.close()

    return admin_count


if __name__ == "__main__":
    create_database()

    print("Database created successfully!")