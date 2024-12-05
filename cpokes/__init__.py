"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Init file, stores app factory for site
"""
import base64

from flask import Flask
import os

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'clients.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Creating Images directory
    app.config["Images"] = "Images"

    def encode_image_directory():
        image_directory = os.path.join(app.config["Images"])
        image_files = os.listdir(image_directory)
        images = {}

        for filename in image_files:
            file_path = os.path.join(image_directory, filename)
            with open(file_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
                encoded_image = encoded_image.replace('\n', '')
                image_url = 'data:image/png;base64,' + encoded_image
                images[filename] = image_url
        return images

    from . import db
    db.init_app(app)

    from . import landing
    app.register_blueprint(landing.bp)
    app.add_url_rule('/', endpoint='index')

    from . import requests
    app.register_blueprint(requests.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    return app

