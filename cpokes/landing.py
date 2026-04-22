"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""
import os
from flask import Flask, Blueprint, render_template

bp = Blueprint("landing", __name__)
app = Flask(__name__)


@bp.route("/")
def landing():
    """
    Prepares landing page
    """
    return render_template("landing.html")


@bp.route("/portfolio")
def portfolio():
    """
    Prepares portfolio page
    """
    image_folder = os.path.join(app.static_folder, 'portfolio')
    images = os.listdir(image_folder)

    return render_template("portfolio.html", images=images)


@bp.route("/faq")
def faq():
    """
    Serves the FAQ page
    """
    return render_template("faq.html")
