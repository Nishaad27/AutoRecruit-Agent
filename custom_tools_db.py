from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import sqlite3
import pandas as pd
import csv
import re
import tempfile

class CSVToSQLiteInput(BaseModel):
    """Input schema for CSVToSQLiteTool."""
    csv_file: str = Field(..., description="Path to the CSV file")
    db_name: str = Field(..., description="Name of the SQLite database")

class CSVToSQLiteTool(BaseTool):
    name: str = "CSV to SQLite"
    description: str = "Reads a CSV file and inserts its data into an SQLite database table called SHORTLISTED_CANDIDATES."
    args_schema: Type[BaseModel] = CSVToSQLiteInput

    def clean_and_format_csv(self, input_file: str) -> str:
        """
        Cleans and formats a raw CSV file by:
        1. Removing unwanted ```csv and ``` markers.
        2. Ensuring proper CSV structure.
        """
        with open(input_file, "r", encoding="utf-8") as infile:
            lines = infile.readlines()

        # Remove ```csv and ``` markers
        cleaned_lines = [re.sub(r"^```csv\n|```$", "", line.strip()) for line in lines if line.strip()]
        
        # Create a temporary file to store cleaned CSV
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", newline="", encoding="utf-8")
        
        csv_reader = csv.reader(cleaned_lines)
        csv_writer = csv.writer(temp_file)

        try:
            headers = next(csv_reader)  # Read headers
            csv_writer.writerow(headers)

            for row in csv_reader:
                csv_writer.writerow(row)

            temp_file.close()
            return temp_file.name  # Return path to cleaned file
        except Exception as e:
            temp_file.close()
            raise Exception(f"Error cleaning CSV: {str(e)}")

    def _run(self, csv_file: str, db_name: str) -> str:
        try:
            # Clean CSV file and get path to cleaned version
            cleaned_csv = self.clean_and_format_csv(csv_file)

            # Read cleaned CSV into a DataFrame
            df = pd.read_csv(cleaned_csv)

            # Keep only the required columns
            required_columns = ["NAME", "MATCH_PERCENTAGE", "RESUME_CONTENT"]
            df = df[required_columns]

            # Drop rows with any missing values
            df = df.dropna()

            # Ensure MATCH_PERCENTAGE is numeric
            df["MATCH_PERCENTAGE"] = pd.to_numeric(df["MATCH_PERCENTAGE"], errors='coerce')

            # Drop rows where MATCH_PERCENTAGE couldn't be converted
            df = df.dropna()

            # Establish SQLite connection
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # Drop table if it exists
            cursor.execute("DROP TABLE IF EXISTS SHORTLISTED_CANDIDATES")

            # Create the table
            create_table_query = """
            CREATE TABLE SHORTLISTED_CANDIDATES (
                NAME TEXT,
                MATCH_PERCENTAGE NUMERIC,
                RESUME_CONTENT TEXT
            );
            """
            cursor.execute(create_table_query)

            # Insert data
            df.to_sql('SHORTLISTED_CANDIDATES', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
            return "Data successfully inserted into a fresh SHORTLISTED_CANDIDATES table."
        except Exception as e:
            return f"Error: {str(e)}"
