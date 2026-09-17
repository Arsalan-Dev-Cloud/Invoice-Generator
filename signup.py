from flask import request, render_template, redirect, flash
from werkzeug.security import generate_password_hash

from database import create_user, get_user_by_email


def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check password confirmation
        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect("/signup")

        # Check whether email already exists
        existing_user = get_user_by_email(email)

        if existing_user:

            flash("An account with this email already exists.")

            return redirect("/signup")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user
        create_user(
            name,
            email,
            hashed_password
        )

        flash("Account created successfully. Please login.")

        return redirect("/login")

    return render_template("signup.html")