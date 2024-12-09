"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Admin page, functions to get tattoo artist to view all request forms
"""
import functools
from io import BytesIO
from flask import (
    Blueprint, flash, g, redirect, render_template, session, request, url_for, send_from_directory, current_app
)
import os
from cpokes.db import get_db
from werkzeug.security import check_password_hash

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
@bp.route('/admin/index')
def index():

    if session.get('user_id') == 1:
        current_requests = get_requests()
        return render_template('auth/index.html', current_requests=current_requests)
    else:
        return redirect(url_for('admin.login'))
