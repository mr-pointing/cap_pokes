"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Email functions page, contains all the functions needed to send emails
"""
from googleapiclient.errors import HttpError
import yagmail
from cpokes.db import artist_json
from flask import url_for

# Sends request form to user
def send_request_email(request_form):
    artist_info = artist_json()

    receiver = request_form.form["email"]
    body = f"Thanks for requesting to book a tattoo with me! I should get back to your request in 3 - 5 days.\n\n"\
           f"Your Request Form:\n"\
           f"<strong>Name:</strong> {request_form.form['name']}\n"\
           f"<strong>Email</strong>: {request_form.form['email']}\n"\
           f"<strong>Pronouns:</strong> {request_form.form['pronouns']}\n"\
           f"<strong>References:</strong> {request_form.form['custom_idea']}\n"\
           f"<strong>Size:</strong> {request_form.form['size']}\n"\
           f"<strong>Placement:</strong> {request_form.form['placement']}\n"\
           f"<strong>Budget:</strong> {request_form.form['budget']}\n"
    try:
        yag = yagmail.SMTP(artist_info['artist_email'], artist_info['yag_pw'])
        yag.send(
            to=receiver,
            subject="Booking Request Information",
            contents=body
        )
    except HttpError as error:
        print(f"An error occurred: {error}")

# Sends notification to artist about their being a new request
def send_request_updates(request_form):
    artist_info = artist_json()

    receiver = artist_info['artist_email']
    body = (f"You've got a new request from {request_form.form['name']}! Check it out: "
            f"https://www.capricornpokes.com{url_for('admin.login')}")

    try:
        yag = yagmail.SMTP(artist_info['email_for_artist'], artist_info['efa_pw'])
        yag.send(
            to=receiver,
            subject=f"You've got a new request from {request_form.form['name']}!",
            contents=body,
        )

    except HttpError as error:
        print(f"An error occurred: {error}")

def send_booking_form(client_email, booking_link):
    artist_info = artist_json()

    receiver = client_email
    body = f"Thanks for requesting a tattoo with me! Happy to say I'd like to book a tattoo with you!"\
           f"See attached form to get started: {booking_link}\n"

    try:
        yag = yagmail.SMTP(artist_info['artist_email'], artist_info['yag_pw'])
        yag.send(
            to=receiver,
            subject="Booking Confirmation Link",
            contents=body
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
