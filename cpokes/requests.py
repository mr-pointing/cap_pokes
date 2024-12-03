"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""
from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)
import os
from cpokes.db import get_db

bp = Blueprint('requests', __name__)


@bp.route('/requests', methods=['GET', 'POST'])
def request_tattoo():
    if request.method == 'POST':
        db = get_db()
        error = None

        if request.form['flash-or-custom'] == 'Flash':
            flash_custom = 0
            custom_idea = ""
        else:
            flash_custom = 1
            custom_idea = request.form['custom_idea']
            custom_reference = request.form['cust_reference']

        if custom_idea:
            reference = custom_reference
        else:
            reference = request.form['reference']
        size = request.form['size']
        placement = request.form['placement']
        budget = request.form['budget']

        client_email = request.form['email']
        existing_client = db.execute('SELECT * FROM client WHERE email=?', (client_email,)).fetchone()

        if existing_client:
            uid_row = db.execute('SELECT uid FROM client WHERE email=?', (client_email,)).fetchone()
            uid = uid_row['uid'] if uid_row else None
            if error is None:
                try:
                    db.execute(
                        'INSERT INTO requests (uid, flash_custom, custom_idea, size, placement, budget, reference) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (uid, flash_custom, custom_idea, size, placement, budget, reference),
                    )
                    db.commit()
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
                        'INSERT INTO requests (uid, flash_custom, custom_idea, size, placement, budget, reference) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (uid, flash_custom, custom_idea, size, placement, budget, reference),
                    )
                    db.commit()
                except db.IntegrityError:
                    error = "Something went wrong!"
                else:
                    return render_template('landing.html')

    return render_template('request.html')
