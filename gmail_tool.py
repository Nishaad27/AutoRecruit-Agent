from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from gmail_utility import authenticate_gmail, create_message, send_message
# from agentops import record_tool

class GmailToolInput(BaseModel):
    """Input schema for GmailTool."""
    receiver_email: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The body of the email to send.")

# @record_tool("This is used for gmail draft emails.")
class GmailTool(BaseTool):
    name: str = "GmailTool"
    description: str = "Useful for sending emails using Gmail API."
    args_schema: Type[BaseModel] = GmailToolInput

    def _run(self, receiver_email: str, subject: str, body: str) -> str:
        try:
            service = authenticate_gmail()

            sender = "nishaadmishra27@gmail.com"
            message = create_message(sender, receiver_email, subject, body)
            sent_msg = send_message(service, "me", message)

            return f"Email sent successfully! Message ID: {sent_msg['id']}"
        except Exception as e:
            return f"Error sending email: {e}"
