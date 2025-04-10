from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from gmail_utility import authenticate_gmail, create_message, send_message

class GmailToolInput(BaseModel):
    """Input schema for GmailTool."""
    receiver_emails: list[str] = Field(..., description="List of recipient email addresses.")
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The body of the email to send.")

class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = "Useful for sending emails to multiple recipients using Gmail API."
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, receiver_emails: list[str], subject: str, body: str) -> str:
        try:
            service = authenticate_gmail()
            sender = "nishaadmishra27@gmail.com"
            results = []

            for email in receiver_emails:
                message = create_message(sender, email, subject, body)
                sent_msg = send_message(service, "me", message)
                if sent_msg:
                    results.append(f"{email} ✅ (Message ID: {sent_msg['id']})")
                else:
                    results.append(f"{email} ❌ Failed to send")

            return "Email sending report:\n" + "\n".join(results)
        except Exception as e:
            return f"Error sending emails: {e}"


