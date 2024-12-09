import os.path
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage

SCOPES = ['https://mail.google.com/']


# Sends request form to user
def send_request_email(request_form):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(f"Thanks for requesting to book a tattoo with me! I should"
                            f"get back to your request in 3 - 5 days.\n\n"
                            f"Your Request Form:"
                            f"Name: {request_form.form['name']}\n"
                            f"Email: {request_form.form['email']}\n"
                            f"Pronouns: {request_form.form['pronouns']}\n"
                            f"References: {request_form.form['custom_idea']}\n"
                            f"Size: {request_form.form['size']}\n"
                            f"Placement: {request_form.form['placement']}\n"
                            f"Budget: {request_form.form['budget']}\n")

        message["To"] = request_form.form['email']
        message["From"] = "jdogthegreat4334@gmail.com"
        message["Subject"] = "Testing client request forms!"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')

    except HttpError as error:
        print(f"An error occurred: {error}")


def send_request_updates(request_form):
    # Opens JSON file with artist info
    file_path = Path(__file__).parent / "artist_info.json"
    with open(file_path, "r") as f:
        artist_info = json.load(f)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(f"You've got a new request form!\n\n"
                            f"Your Request Form:"
                            f"Name: {request_form.form['name']}\n"
                            f"Email: {request_form.form['email']}\n"
                            f"Pronouns: {request_form.form['pronouns']}\n"
                            f"References: {request_form.form['custom_idea']}\n"
                            f"Size: {request_form.form['size']}\n"
                            f"Placement: {request_form.form['placement']}\n"
                            f"Budget: {request_form.form['budget']}\n")

        message["To"] = artist_info['artist_email']
        message["From"] = "jdogthegreat4334@gmail.com"
        message["Subject"] = "Testing notification on new request form!"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')

    except HttpError as error:
        print(f"An error occurred: {error}")
