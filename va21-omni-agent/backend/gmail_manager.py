from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google_auth
import base64
import email

class GmailManager:
    def __init__(self):
        self.credentials = google_auth.get_credentials()
        if self.credentials:
            self.service = build('gmail', 'v1', credentials=self.credentials)
        else:
            self.service = None

    def check_email(self, query=""):
        """Searches for emails matching a query and returns a summary of the results."""
        if not self.service:
            return "Gmail not connected. Please connect your Google account in the settings."

        try:
            # Search for messages
            result = self.service.users().messages().list(userId='me', q=query, maxResults=5).execute()
            messages = result.get('messages', [])

            if not messages:
                return "No messages found."

            email_summaries = []
            for msg in messages:
                msg_data = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = msg_data.get('payload', {})
                headers = payload.get("headers", [])

                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')

                snippet = msg_data.get('snippet', 'No snippet available.')

                email_summaries.append(f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}\n---")

            return "\n".join(email_summaries)

        except HttpError as error:
            return f"An error occurred: {error}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
