import sqlite3


DATABASE_NAME = "invoices.db"


def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    # Invoice table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            invoice_number TEXT UNIQUE,

            customer_name TEXT NOT NULL,

            customer_email TEXT NOT NULL,

            invoice_date TEXT NOT NULL,

            subtotal REAL NOT NULL,

            gst REAL NOT NULL,

            grand_total REAL NOT NULL

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

    connection.commit()

    connection.close()

def save_invoice(
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
            invoice_number,
            customer_name,
            customer_email,
            invoice_date,
            subtotal,
            gst,
            grand_total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
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

def get_all_invoices():

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
        ORDER BY id DESC
    """)

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

def get_invoice_statistics():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(grand_total), 0),
            COALESCE(SUM(gst), 0),
            COALESCE(AVG(grand_total), 0)
        FROM invoices
    """)

    result = cursor.fetchone()

    connection.close()

    return {
        "total_invoices": result[0],
        "total_revenue": result[1],
        "total_gst": result[2],
        "average_invoice": result[3]
    }

def get_monthly_statistics():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            substr(invoice_date, 4, 7) AS month,
            COUNT(*) AS invoice_count,
            SUM(grand_total) AS revenue
        FROM invoices
        GROUP BY substr(invoice_date, 4, 7)
        ORDER BY substr(invoice_date, 7, 4),
                 substr(invoice_date, 4, 2)
    """)

    results = cursor.fetchall()

    connection.close()

    return results

def get_product_statistics():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product_name,
            SUM(quantity) AS total_quantity,
            SUM(total) AS total_revenue
        FROM invoice_items
        GROUP BY product_name
        ORDER BY total_quantity DESC
    """)

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

if __name__ == "__main__":
    create_database()

    print("Database created successfully!")