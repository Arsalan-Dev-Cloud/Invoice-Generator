import sqlite3


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

def get_invoice_details(invoice_id):

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get invoice information
    cursor.execute("""
        SELECT *
        FROM invoices
        WHERE id = ?
    """, (invoice_id,))

    invoice = cursor.fetchone()


    # Get items belonging to this invoice
    cursor.execute("""
        SELECT *
        FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,))

    items = cursor.fetchall()

    connection.close()

    return invoice, items

def delete_invoice(invoice_id):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    # Delete invoice items
    cursor.execute("""
        DELETE FROM invoice_items
        WHERE invoice_id = ?
    """, (invoice_id,))

    # Delete invoice
    cursor.execute("""
        DELETE FROM invoices
        WHERE id = ?
    """, (invoice_id,))

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

if __name__ == "__main__":
    create_database()

    print("Database created successfully!")