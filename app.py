import os

from flask import Flask, render_template, request, send_file, redirect, session
from dotenv import load_dotenv
from pdf_generator import create_invoice_pdf
from database import (
    create_database,
    save_invoice,
    get_all_invoices,
    get_invoice_details,
    delete_invoice,
    get_invoice_statistics,
    get_monthly_statistics,
    get_product_statistics
)
from datetime import datetime
from signup import signup
from login import login
from forgot_password import forgot_password, reset_password

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

create_database()

@app.route("/signup", methods=["GET", "POST"])
def signup_route():

    return signup()


@app.route("/login", methods=["GET", "POST"])
def login_route():

    return login()

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_route():
    return forgot_password()


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_route(token):
    return reset_password(token)

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate_invoice():

    if "user_id" not in session:

        return redirect("/login")

    # -----------------------------
    # Customer Information
    # -----------------------------

    customer_name = request.form["customer_name"]
    customer_email = request.form["customer_email"]


    # -----------------------------
    # Invoice Items
    # -----------------------------

    product_names = request.form.getlist("product_name[]")
    quantities = request.form.getlist("quantity[]")
    prices = request.form.getlist("price[]")


    # -----------------------------
    # Calculate Subtotal
    # -----------------------------

    print("\n----- INVOICE DATA -----")

    print("Customer Name :", customer_name)
    print("Customer Email:", customer_email)

    print("\nItems:")

    subtotal = 0


    for i in range(len(product_names)):

        product = product_names[i]

        quantity = int(quantities[i])

        price = float(prices[i])

        item_total = quantity * price

        subtotal += item_total


        print("-------------------------")

        print("Product :", product)
        print("Quantity:", quantity)
        print("Price   :", price)
        print("Total   :", item_total)


    print("-------------------------")

    print("Subtotal:", subtotal)


    # -----------------------------
    # GST Calculation
    # -----------------------------

    gst_rate = 18

    gst_amount = subtotal * gst_rate / 100

    final_total = subtotal + gst_amount


    print("GST:", gst_amount)

    print("Grand Total:", final_total)


    # -----------------------------
    # Generate PDF
    # -----------------------------

    file_name, invoice_number = create_invoice_pdf(

        customer_name,

        customer_email,

        product_names,

        quantities,

        prices

    )


    # -----------------------------
    # Save Invoice to Database
    # -----------------------------

    invoice_date = datetime.now().strftime("%d-%m-%Y")


    save_invoice(
        session["user_id"],
        invoice_number,
        customer_name,
        customer_email,
        invoice_date,
        subtotal,
        gst_amount,
        final_total,
        product_names,
        quantities,
        prices
    )


    # -----------------------------
    # Download PDF
    # -----------------------------

    return send_file(

        file_name,

        as_attachment=True

    )

@app.route("/history")
def invoice_history():

    if "user_id" not in session:

        return redirect("/login")

    invoices = get_all_invoices(session["user_id"])

    return render_template(
        "history.html",
        invoices=invoices
    )


@app.route("/invoice/<int:invoice_id>")
def invoice_details(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    invoice, items = get_invoice_details(
        invoice_id,
        session["user_id"]
    )

    if invoice is None:
        return redirect("/history")

    return render_template(
        "invoice_details.html",
        invoice=invoice,
        items=items
    )

@app.route("/invoice/<int:invoice_id>/download")
def download_invoice(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    invoice, items = get_invoice_details(
        invoice_id,
        session["user_id"]
    )

    if invoice is None:
        return redirect("/history")

    invoice_number = invoice["invoice_number"]

    file_path = f"invoices/{invoice_number}.pdf"

    return send_file(
        file_path,
        as_attachment=True
    )

@app.route("/invoice/<int:invoice_id>/delete", methods=["POST"])
def delete_invoice_route(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    invoice, items = get_invoice_details(
        invoice_id,
        session["user_id"]
    )

    if invoice:

        invoice_number = invoice["invoice_number"]

        file_path = os.path.join(
            "invoices",
            f"{invoice_number}.pdf"
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        delete_invoice(
            invoice_id,
            session["user_id"]
        )

    return redirect("/history")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    statistics = get_invoice_statistics(
    session["user_id"]
    )

    monthly_statistics = get_monthly_statistics(
        session["user_id"]
    )

    product_statistics = get_product_statistics(
        session["user_id"]
    )

    return render_template(
        "dashboard.html",
        statistics=statistics,
        monthly_statistics=monthly_statistics,
        product_statistics=product_statistics,
        user_name=session["user_name"]
    )

if __name__ == "__main__":

    app.run(debug=True)