from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel
import gspread
import csv
from google.oauth2.service_account import Credentials
import os

class GoogleSheetsInput(BaseModel):
    """Input schema for GoogleSheetsTool."""
    pass

class GoogleSheetsTool(BaseTool):
    name: str = "Google Sheets Data Fetcher"
    description: str = "Fetches all records from a specific hardcoded Google Sheet and saves it as a CSV."
    args_schema: Type[BaseModel] = GoogleSheetsInput

    def _run(self) -> str:
        try:
            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file("recruitment_automation.json", scopes=scopes)
            client = gspread.authorize(creds)

            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            sheet = client.open_by_key(sheet_id)
            data = sheet.sheet1.get_all_records()

            if not data:
                return "The sheet is empty or contains no records."

            # Folder where the CSV will be saved
            output_folder = "output_files"
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # Define the output file path
            csv_file_path = os.path.join(output_folder, "google_sheet_data.csv")

            # Get headers and rows
            headers = data[0].keys()
            rows = [list(row.values()) for row in data]

            # Write the data to a CSV file
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(headers)
                # Write the data rows
                writer.writerows(rows)

            return f"Data has been successfully saved to {csv_file_path}"

        except Exception as e:
            return f"Error fetching Google Sheet: {str(e)}"
