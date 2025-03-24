"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Admin page, functions to get tattoo artist to view all request forms
"""
import uuid
import logging
import requests
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for, send_from_directory, current_app, jsonify
)
from cpokes.db import get_db, artist_json
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import cpokes.email_funcs as ef
from datetime import datetime
import pytz
import os
import random

bp = Blueprint('admin', __name__)


# Log Admin In
@bp.route('/admin', methods=('GET', 'POST'))
def login():
    session.clear()
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


# Checks to see if you're admin, otherwise sent back to the login page
def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') != 1:
            return redirect(url_for('admin.login'))
        return view(**kwargs)

    return wrapped_view


# Retrieve all requests
def get_unbooked_requests():
    db = get_db()
    unbooked_requests = db.execute(
        'SELECT * FROM requests JOIN main.client c ON requests.uid = c.uid WHERE requests.booked = 0 ORDER BY rid DESC'
    ).fetchall()
    return unbooked_requests


# Retrieve all booked appointments
def get_booked():
    db = get_db()

    # Create variable to grab current time, so we only get bookings in the future
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    booked = db.execute(
        'SELECT * FROM bookings JOIN main.client c on bookings.uid = c.uid WHERE date > ? ORDER BY bid DESC', (now,)
    ).fetchall()
    return booked


# Searches table for results
def search_table(column, search_term, table):
    db = get_db()
    query = f'SELECT * FROM {table} JOIN main.client c on {table}.uid = c.uid WHERE {column} LIKE "%{search_term}%"'
    if table == 'requests':
        query += f' AND booked IS 0'
    try:
        search_results = db.execute(query).fetchall()
        return search_results
    except db.IntegrityError as e:
        print(e)


# Search feature for requests
@bp.route('/admin/requests/search', methods=('GET', 'POST'))
@admin_required
def view_searched_requests():
    if request.method == 'POST':
        col = request.form['column']
        term = request.form['search_term']
        answers = search_table(col, term, 'requests')
        results = answers
    else:
        results = []
    return render_template('auth/search_requests.html', results=results)


# Search feature for bookings
@bp.route('/admin/bookings/search', methods=('GET', 'POST'))
@admin_required
def view_searched_bookings():
    if request.method == 'POST':
        col = request.form['column']
        term = request.form['search_term']
        answers = search_table(col, term, 'bookings')
        results = answers
    else:
        results = []
    return render_template('auth/search_bookings.html', results=results)


# Allows Flask to upload images
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# Index
@bp.route('/admin/index', methods=('GET', 'POST'))
@admin_required
def index():
    return render_template('auth/index.html')


# Admins Current Requests
@bp.route('/admin/requests', methods=('GET', 'POST'))
@admin_required
def current_requests():
    if request.method == 'POST':
        request_id = request.form.get('accept_request')
        if request_id:
            return redirect(url_for('admin.booking', request_id=request_id))

    current_reqs = get_unbooked_requests()
    return render_template('auth/current_requests.html', current_requests=current_reqs)


# Admins Current Bookings
@bp.route('/admin/bookings', methods=('GET', 'POST'))
@admin_required
def current_bookings():
    current_booked = get_booked()
    return render_template('auth/current_bookings.html', current_bookings=current_booked)


# Admins Booking platform: sends back to the client a deposit amount and time length
@bp.route('/admin/booking/<int:request_id>', methods=('GET', 'POST'))
@admin_required
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

            db.execute(
                'INSERT INTO bookings (uid, rid, deposit, type, size, placement, budget, token, reference, '
                'link, estimate)'
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (request_for_book['uid'], request_id, request.form.get('deposit'), request.form.get('type'),
                 request_for_book['size'], request_for_book['placement'], request_for_book['budget'], token,
                 request_for_book['reference'], booking_link, request.form.get('estimate')))
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

    if token in booking_tokens and client_info['confirmed'] == 0:
        return render_template('client_booking.html', request=client_info)
    elif token in booking_tokens:
        return render_template('thank_you.html')
    else:
        return redirect(url_for('landing.landing'))


# Updates the booking table with the confirmed booking of tattoo
@bp.route('/admin/update-schedule', methods=('GET', 'POST'))
def update_bookings():
    try:
        # Get info on booking
        data = request.json
        print(data)

        # Strip the prefix for uuid
        e_uuid = data['event_uri'].removeprefix("https://api.calendly.com/scheduled_events/")
        print(e_uuid)
        booking_id = data['booking_id']
        print(booking_id)

        # Use data to get booking date
        artist_info = artist_json()

        url = f"https://api.calendly.com/scheduled_events/{e_uuid}"
        headers = {
            "Authorization": f"Bearer {artist_info['calendly_api_token']}",
            "Content-Type": "application/json"
        }
        params = {"uuid": f"{e_uuid}",
                  "user": f"{artist_info['calendly_user']}"}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            event = response.json()['resource']
            start_time = event['start_time']
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=pytz.UTC)
            eastern = pytz.timezone("US/Eastern")
            local_start_time = start_time.astimezone(eastern)
            print(local_start_time.strftime("%m/%d/%y %I:%M%p"))
            db = get_db()
            db.execute('UPDATE bookings SET date = ? WHERE bid = ?',
                       (local_start_time, booking_id,))
            logging.debug("Bookings date updated")
            db.execute('UPDATE bookings SET confirmed = 1 WHERE bid = ?',
                       (booking_id,))
            logging.debug("Bookings confirmation updated")
            db.commit()

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# Admin Manual Entry form
@bp.route('/admin/manual_form', methods=('GET', 'POST',))
@admin_required
def manual_entry_form():
    if request.method == 'POST':
        db = get_db()
        error = None

        logging.debug(f"Form Data: {request.form}")

        flash_custom = 0 if request.form['flash-or-custom'] == "Flash" else 1
        custom_idea = request.form.get('custom_idea', '')
        uploaded_file = request.files.get('reference') if flash_custom == 0 else request.files.get('cust_reference')

        # Storing uploaded files into uploads directory
        if uploaded_file and uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            uploaded_file.save(file_path)
            reference = f"/uploads/{unique_filename}"
        else:
            reference = None
        logging.debug(f"File path: {reference}")

        m_size = request.form['size']
        m_placement = request.form['placement']
        m_type = request.form.get('type')
        m_deposit = request.form.get('deposit')
        m_estimate = request.form['estimate']
        m_client_email = request.form['email']
        m_rid = random.randint(100, 10000)

        # Generate unique token
        m_token = str(uuid.uuid4())

        # Check if client already exists
        existing_client = db.execute('SELECT * FROM client WHERE email = ?', (m_client_email,)).fetchone()
        logging.debug(f"Client Exists: {existing_client}")

        if existing_client:
            uid_row = db.execute('SELECT uid FROM client WHERE email = ?', (m_client_email,)).fetchone()
            uid = uid_row['uid'] if uid_row else None
            if error is None:
                try:
                    # Generate link
                    m_booking_link = url_for('admin.confirm_booking', token=m_token, _external=True)
                    ef.send_booking_form(m_client_email, m_booking_link)
                    db.execute(
                        'INSERT INTO bookings (uid, rid, deposit, type, size, placement, estimate,'
                        ' token, reference, custom_idea, link)'
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (uid, m_rid, m_deposit, m_type, m_size, m_placement, m_estimate, m_token, reference,
                         custom_idea, m_booking_link)
                    )
                    db.commit()
                    logging.debug("Bookings updated")
                    return render_template('auth/link_page.html', booking_link=m_booking_link)
                except db.IntegrityError as e:
                    print(e)
        else:
            m_name = request.form['name']
            m_phone = request.form['phone']
            m_pronouns = request.form['pronouns']
            db.execute(
                'INSERT INTO client (email, name, phone, pronouns) VALUES (?, ?, ?, ?)',
                (m_client_email, m_name, m_phone, m_pronouns)
            )
            db.commit()
            logging.debug(f"Client entered successfully")
            if error is None:
                uid_row = db.execute('SELECT uid FROM client WHERE email = ?', (m_client_email,)).fetchone()
                uid = uid_row['uid'] if uid_row else None
                try:
                    # Generate link
                    m_booking_link = url_for('admin.confirm_booking', token=m_token, _external=True)
                    ef.send_booking_form(m_client_email, m_booking_link)
                    db.execute(
                        'INSERT INTO bookings (uid, rid, deposit, type, size, placement, estimate,'
                        ' token, reference, custom_idea, link)'
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (uid, m_rid, m_deposit, m_type, m_size, m_placement, m_estimate, m_token, reference,
                         custom_idea, m_booking_link)
                    )
                    db.commit()
                    logging.debug("Bookings updated")
                    return render_template('auth/link_page.html', booking_link=m_booking_link)
                except db.IntegrityError as e:
                    print(e)

    return render_template('auth/manual_entry.html')
