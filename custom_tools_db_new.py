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
    description: str = "Reads a clean CSV file and inserts only NAME, MATCH_PERCENTAGE, EMAIL_ADDRESS, and RESUME_CONTENT into an SQLite database table called SHORTLISTED_CANDIDATES."
    args_schema: Type[BaseModel] = CSVToSQLiteInput

    def _run(self, csv_file: str, db_name: str) -> str:
        try:
            # Read the CSV directly
            df = pd.read_csv(csv_file)

            # Only required columns
            required_columns = ["NAME", "MATCH_PERCENTAGE", "EMAIL_ADDRESS", "RESUME_CONTENT"]
            df = df[required_columns]

            # Drop rows with missing NAME or MATCH_PERCENTAGE
            df = df.dropna(subset=["NAME", "MATCH_PERCENTAGE"])

            # Ensure MATCH_PERCENTAGE is numeric
            df["MATCH_PERCENTAGE"] = pd.to_numeric(df["MATCH_PERCENTAGE"], errors='coerce')

            # Drop rows where conversion failed
            df = df.dropna(subset=["MATCH_PERCENTAGE"])

            # Connect to SQLite and create table
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS SHORTLISTED_CANDIDATES")

            create_table_query = """
            CREATE TABLE SHORTLISTED_CANDIDATES (
                NAME TEXT,
                MATCH_PERCENTAGE NUMERIC,
                EMAIL_ADDRESS TEXT,
                RESUME_CONTENT TEXT
            );
            """
            cursor.execute(create_table_query)

            # Insert into table
            df.to_sql('SHORTLISTED_CANDIDATES', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
            return "Data successfully inserted into SHORTLISTED_CANDIDATES table with selected columns."
        except Exception as e:
            return f"Error: {str(e)}"
