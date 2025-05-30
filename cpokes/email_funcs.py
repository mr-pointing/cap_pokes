"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Email functions page, contains all the functions needed to send emails
"""

import yagmail
from flask import url_for
from googleapiclient.errors import HttpError

from cpokes.db import artist_json


def send_request_email(request_form):
    """
    Sends request form to user
    """
    artist_info = artist_json()

    receiver = request_form.form["email"]
    body = (
        f"Thanks for requesting to book a tattoo with me! I should get back to your request in 3 - 5 days.\n\n"
        f"Your Request Form:\n"
        f"<strong>Name:</strong> {request_form.form['name']}\n"
        f"<strong>Email</strong>: {request_form.form['email']}\n"
        f"<strong>Pronouns:</strong> {request_form.form['pronouns']}\n"
        f"<strong>References:</strong> {request_form.form['custom_idea']}\n"
        f"<strong>Size:</strong> {request_form.form['size']}\n"
        f"<strong>Placement:</strong> {request_form.form['placement']}\n"
        f"<strong>Budget:</strong> {request_form.form['budget']}\n"
    )
    try:
        yag = yagmail.SMTP(artist_info["artist_email"], artist_info["yag_pw"])
        yag.send(to=receiver, subject="Booking Request Information", contents=body)
    except HttpError as error:
        print(f"An error occurred: {error}")


def send_request_updates(request_form):
    """
    Sends notification to artist about their being a new request
    """
    artist_info = artist_json()

    receiver = artist_info["artist_email"]
    body = (
        f"You've got a new request from {request_form.form['name']}! Check it out: "
        f"https://www.capricornpokes.com{url_for('admin.login')}"
    )

    try:
        yag = yagmail.SMTP(artist_info["email_for_artist"], artist_info["efa_pw"])
        yag.send(
            to=receiver,
            subject=f"You've got a new request from {request_form.form['name']}!",
            contents=body,
        )

    except HttpError as error:
        print(f"An error occurred: {error}")


def send_booking_form(client_email, booking_link):
    """
    Sends an email to the client after accepting request
    """
    artist_info = artist_json()

    receiver = client_email
    body = (
        "Thank you so much for filling out a form requesting a tattoo appointment! "
        "I’m happy to work on this project with you.\n\nHere is a link to my booking calendar "
        "as well as an estimate price for your tattoo. Once you’ve booked, you'll receive a "
        "confirmation email with the studio address and all the details. "
        "If you have any questions, please reach out to capricornpokes@gmail.com. "
        "Excited to work with you on this!\n\n"
        f"{booking_link}"
    )

    try:
        yag = yagmail.SMTP(artist_info["artist_email"], artist_info["yag_pw"])
        yag.send(to=receiver, subject="Booking Confirmation Link", contents=body)
    except HttpError as error:
        print(f"An error occurred: {error}")
