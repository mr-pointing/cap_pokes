"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Init file, stores app factory for site
"""

import base64
import os

from flask import Flask


def create_app(test_config=None):
    """
    Application factory
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "clients.sqlite"),
        # Mappings for image folder
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    from . import landing

    app.register_blueprint(landing.bp)
    app.add_url_rule("/", endpoint="index")

    from . import requests

    app.register_blueprint(requests.bp)

    from . import admin

    app.register_blueprint(admin.bp)

    return app
