from flask import request, render_template, redirect, flash
from werkzeug.security import generate_password_hash
from database import (
    get_user_by_email,
    create_password_reset_token,
    get_password_reset_token,
    mark_reset_token_used,
    update_user_password
)

import secrets
from datetime import datetime, timedelta


def forgot_password():

    if request.method == "POST":

        email = request.form["email"]

        # Find user
        user = get_user_by_email(email)

        # Do not reveal whether email exists
        if user:

            # Generate secure reset token
            token = secrets.token_urlsafe(32)

            # Token expires after 15 minutes
            expires_at = datetime.now() + timedelta(minutes=15)

            # Save token
            create_password_reset_token(
                user["id"],
                token,
                expires_at.isoformat()
            )

            # For local testing
            reset_link = f"http://127.0.0.1:5000/reset-password/{token}"

            print("\n===================================")
            print("PASSWORD RESET LINK")
            print("===================================")
            print(reset_link)
            print("===================================\n")

        flash(
            "If an account exists with this email, "
            "a password reset link has been generated."
        )

        return redirect("/forgot-password")

    return render_template("forgot_password.html")


def reset_password(token):

    reset_token = get_password_reset_token(token)

    # Check whether token exists
    if reset_token is None:

        flash("Invalid password reset link.")

        return redirect("/forgot-password")

    # Check whether token was already used
    if reset_token["used"] == 1:

        flash("This password reset link has already been used.")

        return redirect("/forgot-password")

    # Check token expiry
    expires_at = datetime.fromisoformat(
        reset_token["expires_at"]
    )

    if datetime.now() > expires_at:

        flash("This password reset link has expired.")

        return redirect("/forgot-password")

    # Reset password
    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check passwords
        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect(
                f"/reset-password/{token}"
            )

        # Hash new password
        hashed_password = generate_password_hash(password)

        # Update password
        update_user_password(
            reset_token["user_id"],
            hashed_password
        )

        # Mark token as used
        mark_reset_token_used(token)

        flash(
            "Password reset successfully. "
            "You can now login."
        )

        return redirect("/login")

    return render_template(
        "reset_password.html",
        token=token
    )