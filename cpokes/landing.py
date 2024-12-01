"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""
from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)
import os

bp = Blueprint('landing', __name__)


@bp.route('/')
def landing():  # put application's code here
    return render_template('landing.html')

