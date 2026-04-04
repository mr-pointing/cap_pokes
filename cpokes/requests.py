"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Requests page, functions to request tattoos
"""

import logging
import os
import uuid
import sqlite3
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
    error = None
    upload_folder = current_app.config["UPLOAD_FOLDER"]

    if request.method == "POST":
        db = get_db()

        flash_custom = 0 if request.form["flash-or-custom"] == "Flash" else 1
        custom_idea = request.form.get("custom_idea", "").strip()

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

        size = request.form['size']
        placement = request.form['placement']
        budget = request.form['budget']
        client_email = request.form['email']

        if not uploaded_file or uploaded_file.filename == "":
            if flash_custom == 0:
                error = "A flash screenshot is required."
            else:
                error = "A custom reference image is required."

        if error is not None:
            return render_template("request.html", error=error)

        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(uploaded_file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        uploaded_file.save(file_path)
        reference = f"/uploads/{unique_filename}"

        if uploaded_file2 and uploaded_file2.filename != "":
            filename2 = secure_filename(uploaded_file2.filename)
            unique_filename2 = f"{uuid.uuid4()}_{filename2}"
            file_path2 = os.path.join(upload_folder, unique_filename2)
            uploaded_file2.save(file_path2)
            reference2 = f"/uploads/{unique_filename2}"
        else:
            reference2 = None

        logging.debug("Form data: %s", request.form)
        logging.debug("Primary file path: %s", reference)
        logging.debug("Secondary file path: %s", reference2)

        existing_client = db.execute(
            "SELECT uid FROM client WHERE email = ?",
            (client_email,),
        ).fetchone()

        try:
            if existing_client:
                uid = existing_client["uid"]
            else:
                name = request.form["name"]
                alt_name = request.form["alt_name"]
                phone = request.form["phone"]
                pronouns = request.form["pronouns"]

                db.execute(
                    "INSERT INTO client (email, name, alt_name, phone, pronouns) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (client_email, name, alt_name, phone, pronouns),
                )
                db.commit()

                uid_row = db.execute(
                    "SELECT uid FROM client WHERE email = ?",
                    (client_email,),
                ).fetchone()
                uid = uid_row["uid"]

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

            logging.debug("Request inserted successfully.")
            return render_template("request_ty.html")

        except sqlite3.IntegrityError as e:
            logging.error("Database error while creating request: %s", e)
            error = "Something went wrong while submitting your request."

    return render_template("request.html", error=error)
