import os

from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, session, flash
from dotenv import load_dotenv
from pdf_generator import create_invoice_pdf

from database import (
    create_database,
    save_invoice,
    update_invoice_pdf_public_id,
    get_all_invoices,
    get_invoice_details,
    delete_invoice,
    get_invoice_statistics,
    get_monthly_statistics,
    get_product_statistics,
    get_total_users,
    get_total_invoices,
    get_total_revenue,
    get_all_users,
    get_all_invoices_admin,
    delete_user_account,
    update_user_name,
    get_admin_count,
    get_normal_user_count,
    get_user_details_admin,
    get_invoice_details_admin,
    get_deleted_invoices,
    restore_invoice,
    permanently_delete_invoice,
    log_activity,
    get_recent_activity
)



from datetime import datetime
from signup import signup
from login import login
from forgot_password import forgot_password, reset_password

load_dotenv()

import cloudinary
import cloudinary.uploader
import cloudinary.utils

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

def upload_invoice_to_cloudinary(file_path, user_id, invoice_number):

    upload_result = cloudinary.uploader.upload(
        file_path,
        resource_type="raw",
        type="authenticated",
        folder="invoice_generator/invoices",
        public_id=f"user_{user_id}_{invoice_number}"
    )

    return upload_result["public_id"]


@app.after_request
def add_security_headers(response):

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response

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


@app.route("/delete-account")
def delete_account_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("delete_account.html")

@app.route("/delete-account", methods=["POST"])
def delete_account():

    if "user_id" not in session:
        return redirect("/login")

    password = request.form["password"]

    user_id = session["user_id"]

    from database import get_user_by_email

    user = get_user_by_email(
        session["user_email"]
    )

    if user is None:
        session.clear()
        return redirect("/")

    if not check_password_hash(
        user["password"],
        password
    ):
        flash("Incorrect password. Account was not deleted.")
        return redirect("/delete-account")

    # Prevent deleting the last administrator
    if user["role"] == "admin":

        admin_count = get_admin_count()

        if admin_count <= 1:

            flash(
                "The last administrator account cannot be deleted."
            )

            return redirect("/delete-account")

    delete_user_account(user_id)

    session.clear()

    flash(
        "Your account and all associated data have been permanently deleted."
    )

    return redirect("/")

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.")

    return redirect("/")


@app.route("/")
def home():

    return render_template("landing.html")


@app.route("/create-invoice")
def create_invoice():

    if "user_id" not in session:
        return redirect("/login")

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
        session["user_id"],
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


    invoice_id = save_invoice(
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
    # Upload PDF to Cloudinary
    # -----------------------------

    pdf_public_id = upload_invoice_to_cloudinary(
        file_name,
        session["user_id"],
        invoice_number
    )

    # -----------------------------
    # Save Cloudinary ID to database
    # -----------------------------

    update_invoice_pdf_public_id(
        invoice_id,
        pdf_public_id
    )

    log_activity(
        session["user_id"],
        "invoice_created",
        f"Invoice {invoice_number} created"
    )

    return redirect(f"/invoice/{invoice_id}")


@app.route("/history")
def invoice_history():

    if "user_id" not in session:
        return redirect("/login")

    # Admin accounts use the admin dashboard
    if session.get("user_role") == "admin":
        return redirect("/admin")

    invoices = get_all_invoices(
        session["user_id"]
    )

    return render_template(
        "history.html",
        invoices=invoices
    )


@app.route("/trash")
def trash():

    if "user_id" not in session:
        return redirect("/login")

    deleted_invoices = get_deleted_invoices(
        session["user_id"]
    )

    return render_template(
        "trash.html",
        invoices=deleted_invoices
    )


@app.route("/invoice/<int:invoice_id>/restore", methods=["POST"])
def restore_invoice_route(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    deleted_invoices = get_deleted_invoices(user_id)

    invoice = None

    for deleted_invoice in deleted_invoices:

        if deleted_invoice["id"] == invoice_id:
            invoice = deleted_invoice
            break

    if invoice is None:
        return redirect("/trash")

    restore_invoice(
        invoice_id,
        user_id
    )

    log_activity(
        user_id,
        "invoice_restored",
        f"Invoice {invoice['invoice_number']} restored from trash"
    )

    return redirect("/trash")


@app.route("/invoice/<int:invoice_id>/permanent-delete", methods=["POST"])
def permanent_delete_invoice_route(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    deleted_invoices = get_deleted_invoices(user_id)

    invoice = None

    for deleted_invoice in deleted_invoices:

        if deleted_invoice["id"] == invoice_id:
            invoice = deleted_invoice
            break

    if invoice is None:
        return redirect("/trash")

    pdf_path = os.path.join(
        "invoices",
        f"user_{user_id}_{invoice['invoice_number']}.pdf"
    )

    permanently_delete_invoice(
        invoice_id,
        user_id
    )

    log_activity(
        user_id,
        "invoice_permanently_deleted",
        f"Invoice {invoice['invoice_number']} permanently deleted"
    )

    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return redirect("/trash")


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

    pdf_public_id = invoice["pdf_public_id"]

    if not pdf_public_id:
        return redirect(f"/invoice/{invoice_id}")

    download_url, options = cloudinary.utils.cloudinary_url(
        pdf_public_id,
        resource_type="raw",
        type="authenticated",
        secure=True,
        sign_url=True,
        flags="attachment"
    )

    return redirect(download_url)


@app.route("/invoice/<int:invoice_id>/delete", methods=["POST"])
def delete_invoice_route(invoice_id):

    if "user_id" not in session:
        return redirect("/login")

    invoice, items = get_invoice_details(
        invoice_id,
        session["user_id"]
    )

    if invoice:

        delete_invoice(
            invoice_id,
            session["user_id"]
        )

        log_activity(
            session["user_id"],
            "invoice_deleted",
            f"Invoice {invoice['invoice_number']} moved to trash"
        )

    return redirect("/history")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    # Admin accounts use the admin dashboard
    if session.get("user_role") == "admin":
        return redirect("/admin")

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


@app.route("/statistics")
def statistics_page():

    if "user_id" not in session:
        return redirect("/login")

    statistics = get_invoice_statistics(
        session["user_id"]
    )

    return render_template(
        "statistics.html",
        statistics=statistics
    )


@app.route("/monthly-statistics")
def monthly_statistics_page():

    if "user_id" not in session:
        return redirect("/login")

    monthly_statistics = get_monthly_statistics(
        session["user_id"]
    )

    return render_template(
        "monthly_statistics.html",
        monthly_statistics=monthly_statistics
    )


@app.route("/product-sales")
def product_sales_page():

    if "user_id" not in session:
        return redirect("/login")

    product_statistics = get_product_statistics(
        session["user_id"]
    )

    return render_template(
        "product_sales.html",
        product_statistics=product_statistics
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        new_name = request.form["name"].strip()

        if not new_name:
            flash("Name cannot be empty.")
            return redirect("/profile")

        update_user_name(
            session["user_id"],
            new_name
        )

        # Update the current session
        # so the new name appears immediately
        session["user_name"] = new_name

        flash("Your name has been updated successfully.")

        return redirect("/profile")

    from database import get_user_by_email

    user = get_user_by_email(
        session["user_email"]
    )

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        from database import get_user_by_email

        user = get_user_by_email(
            session["user_email"]
        )

        if user is None:
            session.clear()
            return redirect("/")

        # Check current password
        if not check_password_hash(
            user["password"],
            current_password
        ):
            flash("Current password is incorrect.")
            return redirect("/change-password")

        # Check new password confirmation
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect("/change-password")

        # Prevent using the same password
        if check_password_hash(
            user["password"],
            new_password
        ):
            flash("New password must be different from your current password.")
            return redirect("/change-password")

        # Hash new password
        hashed_password = generate_password_hash(
            new_password
        )

        # Update database
        from database import update_user_password

        update_user_password(
            session["user_id"],
            hashed_password
        )

        flash("Your password has been changed successfully.")

        return redirect("/profile")

    return render_template(
        "change_password.html"
    )


@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    total_users = get_total_users()
    normal_users = get_normal_user_count()
    administrators = get_admin_count()

    total_invoices = get_total_invoices()
    total_revenue = get_total_revenue()

    
    return render_template(

        "admin/overview.html",

        user_name=session["user_name"],

        total_users=total_users,

        normal_users=normal_users,

        administrators=administrators,

        total_invoices=total_invoices,

        total_revenue=total_revenue

    )
  


@app.route("/admin/users")
def admin_users():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    users = get_all_users()
    
    return render_template(
        "admin/users.html",
        users=users
    )


@app.route("/admin/users/<int:user_id>")
def admin_user_details(user_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    user = get_user_details_admin(user_id)

    if user is None:
        flash("User not found.")
        return redirect("/admin/users")

    return render_template(
        "admin/user_details.html",
        user=user
    )


@app.route("/admin/invoices/<int:invoice_id>")
def admin_invoice_details(invoice_id):
  
    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    invoice_data = get_invoice_details_admin(invoice_id)

    if invoice_data is None:
        flash("Invoice not found.")
        return redirect("/admin/invoices")

    return render_template(
        "admin/invoice_details.html",
        invoice=invoice_data["invoice"],
        items=invoice_data["items"]
    )
  


@app.route("/admin/invoices")
def admin_invoices():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    invoices = get_all_invoices_admin()

    return render_template(
        "admin/invoices.html",
        invoices=invoices
    )


@app.route("/admin/activity")
def admin_activity():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("user_role") != "admin":
        flash("Access denied.")
        return redirect("/dashboard")

    activities = get_recent_activity(20)

    return render_template(
        "admin/activity.html",
        activities=activities
    )



if __name__ == "__main__":

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )