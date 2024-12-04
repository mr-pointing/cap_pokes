"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Database file, sets up the database for us
"""
import sqlite3
import click
from flask import current_app, g
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))
    init_admin()


@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def init_admin():
    db = get_db()
    username = "admin"
    password = "password"
    hashed = generate_password_hash(password)

    db.execute(
        'INSERT INTO user (username, password) VALUES (?, ?)', (username, hashed)
    )

    db.commit()
    db.close()
