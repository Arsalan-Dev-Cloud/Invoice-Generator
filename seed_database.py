
import getpass
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from database import create_database, get_connection, release_connection


ADMIN_EMAIL = "shaikhmohammadarsalan5@gmail.com"
ADMIN_NAME = "Shaikh Mohammad Arsalan Mohsin"

DEMO_USERS = [
    ("Rahul Sharma", "rahul.demo@example.com"),
    ("Priya Patel", "priya.demo@example.com"),
    ("Amit Verma", "amit.demo@example.com"),
]

CUSTOMERS = [
    ("Tech Solutions", "contact@techsolutions.example"),
    ("Global Traders", "sales@globaltraders.example"),
    ("Digital World", "billing@digitalworld.example"),
    ("Smart Enterprises", "info@smartenterprises.example"),
    ("Creative Studio", "hello@creativestudio.example"),
    ("Modern Electronics", "orders@modernelectronics.example"),
    ("Bright Services", "accounts@brightservices.example"),
    ("Future Systems", "support@futuresystems.example"),
    ("Prime Technologies", "admin@primetech.example"),
    ("City Office Supplies", "sales@citysupplies.example"),
]

PRODUCTS = [
    ("Laptop", 55000.00),
    ("Wireless Mouse", 750.00),
    ("Keyboard", 1500.00),
    ("Monitor", 12500.00),
    ("Printer", 8500.00),
    ("Software License", 4500.00),
    ("USB Drive", 650.00),
    ("Office Chair", 6500.00),
    ("Webcam", 2200.00),
    ("External SSD", 7500.00),
]

ACTIVITIES = [
    ("user_registered", "Demo user account registered"),
    ("login", "User logged in"),
    ("invoice_created", "Created demonstration invoice"),
    ("invoice_created", "Generated customer invoice"),
    ("invoice_deleted", "Moved invoice to trash"),
    ("invoice_restored", "Restored deleted invoice"),
    ("profile_updated", "Updated profile information"),
    ("invoice_created", "Created a new business invoice"),
    ("login", "Logged in to the application"),
    ("invoice_created", "Generated sample invoice"),
]


def main():

    print("\n================================")
    print("   INVOICE GENERATOR DB SEEDER")
    print("================================\n")

    admin_password = getpass.getpass(
        "Enter your ADMIN password: "
    )

    demo_password = getpass.getpass(
        "Enter a password for DEMO accounts: "
    )

    if len(admin_password) < 8 or len(demo_password) < 8:
        print("Passwords must contain at least 8 characters.")
        return

    admin_hash = generate_password_hash(admin_password)
    demo_hash = generate_password_hash(demo_password)

    print("\nInitializing database...")

    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------
        # 1. CREATE ADMIN
        # -----------------------------

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'admin')
            ON CONFLICT (email)
            DO UPDATE SET
                name = EXCLUDED.name,
                role = 'admin'
            RETURNING id
        """, (
            ADMIN_NAME,
            ADMIN_EMAIL,
            admin_hash
        ))

        admin_id = cursor.fetchone()["id"]

        print("Admin account ready.")

        # -----------------------------
        # 2. CREATE DEMO USERS
        # -----------------------------

        demo_user_ids = []

        for name, email in DEMO_USERS:

            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, 'user')
                ON CONFLICT (email)
                DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """, (
                name,
                email,
                demo_hash
            ))

            demo_user_ids.append(
                cursor.fetchone()["id"]
            )

        print("3 demo users ready.")

        # -----------------------------
        # 3. CREATE INVOICES
        # -----------------------------

        invoice_count = 0
        item_count = 0

        for user_index, user_id in enumerate(demo_user_ids):

            for number in range(1, 6):

                customer_index = (
                    user_index * 5 + number - 1
                )

                customer_name, customer_email = CUSTOMERS[
                    customer_index% len(CUSTOMERS)
                ]

                invoice_number = f"INV-{number:03d}"

                selected_products = [
                    PRODUCTS[(customer_index + number) % len(PRODUCTS)],
                    PRODUCTS[(customer_index + number + 3) % len(PRODUCTS)]
                ]

                subtotal = sum(
                    price * quantity
                    for (_, price), quantity in zip(
                        selected_products,
                        [2, 1]
                    )
                )

                subtotal = round(subtotal, 2)
                gst = round(subtotal * 0.18, 2)
                grand_total = round(subtotal + gst, 2)

                invoice_date = (
                    datetime.now() - timedelta(
                        days=customer_index * 4
                    )
                ).strftime("%d-%m-%Y")

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
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id, invoice_number)
                    DO NOTHING
                    RETURNING id
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

                invoice = cursor.fetchone()

                if invoice is None:
                    continue

                invoice_id = invoice["id"]
                invoice_count += 1

                # Insert invoice items

                for item_index, (product, price) in enumerate(
                    selected_products
                ):

                    quantity = [2, 1][item_index]
                    total = round(quantity * price, 2)

                    cursor.execute("""
                        INSERT INTO invoice_items (
                            invoice_id,
                            product_name,
                            quantity,
                            price,
                            total
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        invoice_id,
                        product,
                        quantity,
                        price,
                        total
                    ))

                    item_count += 1

            # Keep invoice numbering synchronized

            cursor.execute("""
                INSERT INTO invoice_counters (
                    user_id,
                    last_invoice_number
                )
                VALUES (%s, 5)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    last_invoice_number = GREATEST(
                        invoice_counters.last_invoice_number,
                        EXCLUDED.last_invoice_number
                    )
            """, (user_id,))

        print("Sample invoices and items prepared.")

        # -----------------------------
        # 4. CREATE ACTIVITY LOGS
        # -----------------------------

        for index, (action, description) in enumerate(ACTIVITIES):

            log_description = (
                f"SEED DEMO: {description}"
            )

            cursor.execute("""
                INSERT INTO activity_logs (
                    user_id,
                    action,
                    description
                )
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM activity_logs
                    WHERE description = %s
                )
            """, (
                demo_user_ids[index % len(demo_user_ids)],
                action,
                log_description,
                log_description
            ))

        connection.commit()

        print("\n================================")
        print("       SEEDING SUCCESSFUL")
        print("================================")
        print(f"Admin: {ADMIN_EMAIL}")
        print(f"Demo users: {len(demo_user_ids)}")
        print(f"New invoices: {invoice_count}")
        print(f"New invoice items: {item_count}")
        print(f"Activity logs: {len(ACTIVITIES)}")
        print("================================\n")

    except Exception as error:

        connection.rollback()

        print("\nSeeding failed:", error)

        raise

    finally:

        cursor.close()
        release_connection(connection)


if __name__ == "__main__":
    main()
