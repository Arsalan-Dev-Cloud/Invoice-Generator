from flask import request, render_template, redirect, session, flash
from werkzeug.security import check_password_hash

from database import get_user_by_email, log_activity


def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user
        user = get_user_by_email(email)

        if user is None:

            flash("Invalid email or password.")

            return redirect("/login")

        # Check password
        if not check_password_hash(
            user["password"],
            password
        ):

            flash("Invalid email or password.")

            return redirect("/login")

        # Store user information in session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        session["user_email"] = user["email"]
        session["user_role"] = user["role"]

        log_activity(
            user["id"],
            "login",
            "User logged in"
        )

        if user["role"] == "admin":
            return redirect("/admin")

        return redirect("/dashboard")

    return render_template("login.html")