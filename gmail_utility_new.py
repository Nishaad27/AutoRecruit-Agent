import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import markdown

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        {final_email_body}
    </body>
    </html>
"""

def authenticate_gmail():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(current_dir, 'token.json')
    credentials_path = os.path.join(current_dir, 'credentials.json')

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. "
                    "Please ensure you have downloaded your OAuth 2.0 credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
    formatted_html = HTML_TEMPLATE.format(final_email_body=md.convert(message_text))

    msg = EmailMessage()
    msg['To'] = to
    msg['From'] = sender
    msg['Subject'] = subject
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(formatted_html)

    encodedMsg = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': encodedMsg}

def send_message(service, user_id, message_body):
    try:
        draft = service.users().drafts().create(userId=user_id, body={'message': message_body}).execute()
        sent_message = service.users().messages().send(userId=user_id, body={'raw': message_body['raw']}).execute()
        print(f"Email sent: Message ID {sent_message['id']}")
        return sent_message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None
