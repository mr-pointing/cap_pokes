"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Landing page, has all the options for all main features
"""
from flask import (
    Blueprint, Flask, g, redirect, render_template, request, session, url_for
)
import os

bp = Blueprint('requests', __name__)


@bp.route('/requests', methods=['GET', 'POST'])
def request_tattoo():
    return render_template('request.html')