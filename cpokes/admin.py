"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Admin page, functions to get tattoo artist to view all request forms
"""
import uuid
import logging
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
def get_unbooked_requests():
    db = get_db()
    unbooked_requests = db.execute(
        'SELECT * FROM requests JOIN main.client c ON requests.uid = c.uid WHERE requests.booked = 0'
    ).fetchall()
    return unbooked_requests


# Retrieve all booked appointments
def get_booked():
    db = get_db()
    booked = db.execute(
        'SELECT * FROM bookings JOIN main.client c on bookings.uid = c.uid'
    ).fetchall()
    return booked

def search_requests(column, search_term):
    db = get_db()
    try:
        search_results = db.execute(
            'SELECT * FROM requests JOIN main.client c on requests.uid = c.uid WHERE ? = ?',
            (column, search_term,)).fetchall()
        return search_results
    except db.IntegrityError as e:
        print(e)


# Allows Flask to upload images
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Index
@bp.route('/admin/index', methods=('GET', 'POST'))
def index():
    if session.get('user_id') == 1:
        return render_template('auth/index.html')
    else:
        return redirect(url_for('admin.login'))


# Admins Current Requests
@bp.route('/admin/current_requests', methods=('GET', 'POST'))
def current_requests():
    if session.get('user_id') == 1:
        if request.method == 'POST':
            request_id = request.form.get('accept_request')
            if request_id:
                return redirect(url_for('admin.booking', request_id=request_id))

        current_reqs = get_unbooked_requests()
        return render_template('auth/current_requests.html', current_requests=current_reqs)
    else:
        return redirect(url_for('admin.login'))

    # Admins Current Requests
@bp.route('/admin/current_bookings', methods=('GET', 'POST'))
def current_bookings():
    if session.get('user_id') == 1:

        current_booked = get_booked()
        return render_template('auth/current_bookings.html', current_bookings=current_booked)
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
        print(f"Type: {request.form.get('type')}")
        # Generate unique token
        token = str(uuid.uuid4())
        # Commit to database
        try:

            # Generate link
            booking_link = url_for('admin.confirm_booking', token=token, _external=True)
            ef.send_booking_form(request_for_book['email'], booking_link)

            db.execute('INSERT INTO bookings (uid, rid, deposit, type, size, placement, budget, token, reference, link)'
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       (request_for_book['uid'], request_id, request.form.get('deposit'), request.form.get('type'),
                        request_for_book['size'], request_for_book['placement'], request_for_book['budget'], token,
                        request_for_book['reference'], booking_link))
            logging.debug("Bookings updated")
            db.execute('UPDATE requests SET booked = 1 WHERE rid = ?',
                       (request_id,))
            logging.debug("Requests updated")
            db.commit()

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


