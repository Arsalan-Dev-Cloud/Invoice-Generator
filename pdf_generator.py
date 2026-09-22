import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime

def get_next_invoice_number(user_id):

    from database import get_connection, release_connection

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Get the last invoice number used by this user
        cursor.execute("""
            SELECT last_invoice_number
            FROM invoice_counters
            WHERE user_id = %s
        """, (user_id,))

        result = cursor.fetchone()

        if result is None:

            number = 1

            cursor.execute("""
                INSERT INTO invoice_counters (
                    user_id,
                    last_invoice_number
                )
                VALUES (%s, %s)
            """, (
                user_id,
                number
            ))

        else:

            number = result["last_invoice_number"] + 1

            cursor.execute("""
                UPDATE invoice_counters
                SET last_invoice_number = %s
                WHERE user_id = %s
            """, (
                number,
                user_id
            ))

        connection.commit()

        return f"INV-{number:03d}"

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()
        release_connection(connection)

def create_invoice_pdf(
    user_id,
    customer_name,
    customer_email,
    product_names,
    quantities,
    prices
):

   # Invoice information
    invoice_number = get_next_invoice_number(user_id)
    invoice_date = datetime.now().strftime("%d-%m-%Y")

    os.makedirs("invoices", exist_ok=True)

    file_name = os.path.join(
        "invoices",
        f"user_{user_id}_{invoice_number}.pdf"
    )
    
    pdf = canvas.Canvas(file_name, pagesize=A4)

    width, height = A4
    

    # -----------------------------
    # Header
    # -----------------------------

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(50, height - 60, "INVOICE")

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 100, "Invoice Generator")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 118, "Pune, Maharashtra")
    pdf.drawString(50, height - 134, "India")

    pdf.drawString(400, height - 100, f"Invoice No: {invoice_number}")
    pdf.drawString(400, height - 118, f"Date: {invoice_date}")

    # -----------------------------
    # Customer Information
    # -----------------------------

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, height - 180, "Bill To:")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 198, customer_name)
    pdf.drawString(50, height - 214, customer_email)

    # -----------------------------
    # Items Table
    # -----------------------------

    table_y = height - 270

    pdf.setFillColor(colors.lightgrey)
    pdf.rect(50, table_y, 495, 25, fill=1)

    pdf.setFillColor(colors.black)

    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(60, table_y + 8, "Product")
    pdf.drawString(300, table_y + 8, "Quantity")
    pdf.drawString(380, table_y + 8, "Price")
    pdf.drawString(470, table_y + 8, "Total")

    # -----------------------------
    # Invoice Items
    # -----------------------------

    pdf.setFont("Helvetica", 10)

    subtotal = 0

    current_y = table_y - 20

    for i in range(len(product_names)):

        product = product_names[i]
        quantity = int(quantities[i])
        price = float(prices[i])

        item_total = quantity * price

        subtotal += item_total

        pdf.drawString(60, current_y, product)
        pdf.drawString(305, current_y, str(quantity))
        pdf.drawString(380, current_y, f"INR {price:.2f}")
        pdf.drawString(470, current_y, f"INR {item_total:.2f}")

        current_y -= 25

    # -----------------------------
    # GST
    # -----------------------------

    gst_rate = 18

    gst_amount = subtotal * gst_rate / 100

    grand_total = subtotal + gst_amount

    # -----------------------------
    # Summary
    # -----------------------------

    summary_y = current_y - 30

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        350,
        summary_y,
        f"Subtotal: INR {subtotal:.2f}"
    )

    pdf.drawString(
        350,
        summary_y - 20,
        f"GST ({gst_rate}%): INR {gst_amount:.2f}"
    )

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(
        350,
        summary_y - 50,
        f"Grand Total: INR {grand_total:.2f}"
    )

    # -----------------------------
    # Footer
    # -----------------------------

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        50,
        50,
        "Thank you for your business!"
    )

    pdf.save()

    return file_name, invoice_number