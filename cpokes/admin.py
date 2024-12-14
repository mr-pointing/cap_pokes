"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Admin page, functions to get tattoo artist to view all request forms
"""
import functools
import json
from pathlib import Path
from io import BytesIO
import uuid
from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for, send_from_directory, current_app
)
import os
from cpokes.db import get_db
from werkzeug.security import check_password_hash
import cpokes.email_funcs as ef
import json

bp = Blueprint('admin', __name__)


# Log Admin In
@bp.route('/admin', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        admin = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if admin is None:
            error = 'Incorrect username'
        elif not check_password_hash(admin['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = admin['id']
            return redirect(url_for('admin.index'))

    return render_template('auth/login.html')


# Log Admin Out
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))


# Retrieve all requests
def get_requests():
    db = get_db()
    current_requests = db.execute(
        'SELECT * FROM requests JOIN main.client c on requests.uid = c.uid'
    ).fetchall()
    return current_requests


# Allows Flask to upload images
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Index
@bp.route('/admin/index', methods=('GET', 'POST'))
def index():
    if session.get('user_id') == 1:
        if request.method == 'POST':
            request_id = request.form.get('accept_request')
            if request_id:
                return redirect(url_for('admin.booking', request_id=request_id))

        current_requests = get_requests()
        return render_template('auth/index.html', current_requests=current_requests)
    else:
        return redirect(url_for('admin.login'))


# Admins Booking platform: sends back to the client a deposit amount and time length
@bp.route('/admin/booking/<int:request_id>', methods=('GET', 'POST'))
def booking(request_id):
    db = get_db()
    request_for_book = db.execute("SELECT * FROM requests JOIN main.client c"
                                  " on requests.uid = c.uid WHERE rid = ?", (request_id,)).fetchone()

    if request.method == "POST":
        print("Post reached")
        print(f"Deposit: {request.form.get('deposit')}")
        print(f"Length: {request.form.get('length')}")
        # Generate unique token
        token = str(uuid.uuid4())
        # Commit to database
        try:
            db.execute('INSERT INTO bookings (uid, rid, deposit, length, size, placement, budget, token, reference) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (request_for_book['uid'], request_id, request.form.get('deposit'), request.form.get('length'),
                        request_for_book['size'], request_for_book['placement'], request_for_book['budget'], token,
                        request_for_book['reference']))
            print("Form data received:")

            db.commit()
            # Generate link
            booking_link = url_for('admin.confirm_booking', token=token, _external=True)
            ef.send_booking_form(request_for_book['email'], booking_link)
            return redirect(url_for('admin.index'))
        except db.IntegrityError as e:
            print(e)

    return render_template('auth/admin_booking.html', request=request_for_book)


# Clients booking platform: allows client to pick a date and time based on artists length
@bp.route('/booking/<token>', methods=('GET', 'POST'))
def confirm_booking(token):
    db = get_db()
    client_info = db.execute('SELECT * FROM bookings JOIN client c on bookings.uid = c.uid WHERE token = ?',
                             (token,)).fetchone()
    booking_tokens = [row['token'] for row in db.execute('SELECT token FROM bookings').fetchall()]

    if token in booking_tokens:
        return render_template('client_booking.html', request=client_info)
    else:
        return redirect(url_for('landing.landing'))


@bp.route('/api/artist-availability')
def artist_availability():
    file_path = Path(__file__).parent / "artist_schedule.json"
    with open(file_path, "r") as f:
        events = json.load(f)

    return events
