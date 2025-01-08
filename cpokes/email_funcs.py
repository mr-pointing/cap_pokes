"""
Title: Capricorn Pokes Booking Site
Author: Richard Pointing
Purpose: Email functions page, contains all the functions needed to send emails
"""
import json
from pathlib import Path
from googleapiclient.errors import HttpError
import yagmail

# Sends request form to user
def send_request_email(request_form):
    # Opens JSON file with artist info
    file_path = Path(__file__).parent / "artist_info.json"
    with open(file_path, "r") as f:
        artist_info = json.load(f)

    receiver = request_form.form["email"]
    body = f"Thanks for requesting to book a tattoo with me! I should"\
           f"get back to your request in 3 - 5 days.\n\n"\
           f"Your Request Form:"\
           f"Name: {request_form.form['name']}\n"\
           f"Email: {request_form.form['email']}\n"\
           f"Pronouns: {request_form.form['pronouns']}\n"\
           f"References: {request_form.form['custom_idea']}\n"\
           f"Size: {request_form.form['size']}\n"\
           f"Placement: {request_form.form['placement']}\n"\
           f"Budget: {request_form.form['budget']}\n"
    try:
        yag = yagmail.SMTP(artist_info['email_for_artist'], artist_info['efa_pw'])
        yag.send(
            to=receiver,
            subject="Thanks for requesting to book a tattoo with me!",
            contents=body
        )
    except HttpError as error:
        print(f"An error occurred: {error}")

# Sends notification to artist about their being a new request
def send_request_updates(request_form):
    # Opens JSON file with artist info
    file_path = Path(__file__).parent / "artist_info.json"
    with open(file_path, "r") as f:
        artist_info = json.load(f)

    receiver = artist_info['email']
    body = "You've got a new request! Check it out: "

    try:
        yag = yagmail.SMTP(artist_info['email_for_artist'], artist_info['efa_pw'])
        yag.send(
            to=receiver,
            subject="You've got a new request!",
            contents=body,
        )

    except HttpError as error:
        print(f"An error occurred: {error}")

def send_booking_form(client_email, booking_link):
    # Opens JSON file with artist info
    file_path = Path(__file__).parent / "artist_info.json"
    with open(file_path, "r") as f:
        artist_info = json.load(f)

    receiver = client_email
    body = f"Thanks for requesting a tattoo with me! Happy to say I'd like to book a tattoo with you!"\
           f"See attached form to get started: {booking_link}\n"

    try:
        yag = yagmail.SMTP(artist_info['email_for_artist'], artist_info['efa_pw'])
        yag.send(
            to=receiver,
            subject="Booking Confirmation Link",
            contents=body
        )
    except HttpError as error:
        print(f"An error occurred: {error}")
