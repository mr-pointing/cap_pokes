"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""
import logging
import cpokes.email_funcs as ef
from flask import (
    Blueprint, Flask, current_app, g, redirect, render_template, request, session, url_for, send_file
)
import os
import uuid
from werkzeug.utils import secure_filename
from cpokes.db import get_db

logging.basicConfig(level=logging.DEBUG)

bp = Blueprint('requests', __name__)


@bp.route('/requests', methods=['GET', 'POST'])
def request_tattoo():
    if request.method == 'POST':
        db = get_db()
        error = None

        flash_custom = 0 if request.form['flash-or-custom'] == 'Flash' else 1
        custom_idea = request.form.get('custom_idea', "")

        uploaded_file = request.files.get('reference') if flash_custom == 0 else request.files.get('cust_reference')

        # Store uploaded images in uploads directory
        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            uploaded_file.save(file_path)
            reference = f"/uploads/{unique_filename}"
        else:
            reference = None

        size = request.form['size']
        placement = request.form['placement']
        budget = request.form['budget']
        client_email = request.form['email']

        logging.debug(f"Form data: {request.form}")
        logging.debug(f"File path: {reference}")

        existing_client = db.execute('SELECT * FROM client WHERE email=?', (client_email,)).fetchone()

        if existing_client:
            uid_row = db.execute('SELECT uid FROM client WHERE email=?', (client_email,)).fetchone()
            uid = uid_row['uid'] if uid_row else None
            if error is None:
                try:
                    db.execute(
                        'INSERT INTO requests (uid, flash_custom, custom_idea, size, placement, budget, reference) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (uid, flash_custom, custom_idea, size, placement, budget, reference),
                    )
                    db.commit()
                    ef.send_request_email(request)
                    ef.send_request_updates(request)
                    logging.debug("Inserted request into requests table.")
                    return redirect(url_for('landing.landing'))
                except db.IntegrityError:
                    error = "Something went wrong!"
                else:
                    return render_template('landing.html')
        else:
            name = request.form['name']
            phone = request.form['phone']
            pronouns = request.form['pronouns']
            db.execute(
                'INSERT INTO client (email, name, phone, pronouns) VALUES (?, ?, ?, ?)',
                (client_email, name, phone, pronouns),
            )
            db.commit()
            if error is None:
                try:
                    uid_row = db.execute('SELECT uid FROM client WHERE email=?', (client_email,)).fetchone()
                    uid = uid_row['uid'] if uid_row else None
                    db.execute(
                        'INSERT INTO requests (uid, flash_custom, custom_idea, size, placement, budget, reference) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (uid, flash_custom, custom_idea, size, placement, budget, reference),
                    )
                    db.commit()
                    ef.send_request_email(request)
                    ef.send_request_updates(request)
                    logging.debug("Inserted client and request into requests table.")
                    return redirect(url_for('landing.landing'))
                except db.IntegrityError as e:
                    logging.error(f"Database error: {e}")
                    error = "Something went wrong!"
                else:
                    return render_template('landing.html')

    return render_template('request.html')
