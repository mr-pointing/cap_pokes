"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""

from flask import Blueprint, render_template

bp = Blueprint("landing", __name__)


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
    return render_template("portfolio.html")
