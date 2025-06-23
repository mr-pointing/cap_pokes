"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Requests page, functions to request tattoos
"""

import logging
import os
import uuid

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import cpokes.email_funcs as ef
from cpokes.db import get_db

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint("requests", __name__)


@bp.route("/requests", methods=["GET", "POST"])
def request_tattoo():
    """
    Creates a new client if they don't already exist, then
    takes their information to make a request
    """
    if request.method == "POST":
        db = get_db()
        error = None

        flash_custom = 0 if request.form["flash-or-custom"] == "Flash" else 1
        custom_idea = request.form.get("custom_idea", "")

        uploaded_file = (
            request.files.get("reference")
            if flash_custom == 0
            else request.files.get("cust_reference")
        )
        uploaded_file2 = (
            request.files.get("reference2")
            if flash_custom == 0
            else request.files.get("cust_reference2")
        )

        upload_folder = current_app.config["UPLOAD_FOLDER"]

        # Store uploaded images in uploads directory
        if uploaded_file and uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            uploaded_file.save(file_path)
            reference = f"/uploads/{unique_filename}"
        else:
            reference = None

        if uploaded_file2 and uploaded_file2.filename != "":
            filename = secure_filename(uploaded_file2.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            uploaded_file2.save(file_path)
            reference2 = f"/uploads/{unique_filename}"
        else:
            reference2 = None

        size = request.form["size"]
        placement = request.form["placement"]
        budget = request.form["budget"]
        client_email = request.form["email"]

        logging.debug(f"Form data: {request.form}")
        logging.debug(f"File path: {reference}")
        logging.debug(f"File path for 2: {reference2}")

        existing_client = db.execute(
            "SELECT * FROM client WHERE email=?", (client_email,)
        ).fetchone()
        logging.debug(f"Client Exists: {existing_client}")

        if existing_client:
            uid_row = db.execute(
                "SELECT uid FROM client WHERE email=?", (client_email,)
            ).fetchone()
            uid = uid_row["uid"] if uid_row else None
            if error is None:
                try:
                    db.execute(
                        "INSERT INTO requests (uid, flash_custom, custom_idea, size, "
                        "placement, budget, reference, reference2, booked) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            uid,
                            flash_custom,
                            custom_idea,
                            size,
                            placement,
                            budget,
                            reference,
                            reference2,
                            0,
                        ),
                    )
                    db.commit()
                    ef.send_request_email(request)
                    ef.send_request_updates(request)
                    logging.debug("Inserted request into requests table.")
                    return render_template("request_ty.html")
                except db.IntegrityError:
                    error = "Something went wrong!"

        else:
            name = request.form["name"]
            alt_name = request.form["alt_name"]
            phone = request.form["phone"]
            pronouns = request.form["pronouns"]
            db.execute(
                "INSERT INTO client (email, name, alt_name, phone, pronouns) VALUES (?, ?, ?, ?, ?)",
                (client_email, name, alt_name, phone, pronouns),
            )
            db.commit()
            logging.debug(f"Client entered successfully")
            if error is None:
                try:
                    uid_row = db.execute(
                        "SELECT uid FROM client WHERE email=?", (client_email,)
                    ).fetchone()
                    uid = uid_row["uid"] if uid_row else None
                    db.execute(
                        "INSERT INTO requests (uid, flash_custom, custom_idea, size, "
                        "placement, budget, reference, reference2, booked) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            uid,
                            flash_custom,
                            custom_idea,
                            size,
                            placement,
                            budget,
                            reference,
                            reference2,
                            0,
                        ),
                    )
                    db.commit()
                    ef.send_request_email(request)
                    ef.send_request_updates(request)
                    logging.debug("Inserted client and request into requests table.")
                    return render_template("request_ty.html")
                except db.IntegrityError as e:
                    logging.error(f"Database error: {e}")
                    error = "Something went wrong!"

    return render_template("request.html")
