from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import sqlite3
import pandas as pd

class CSVToSQLiteInput(BaseModel):
    """Input schema for CSVToSQLiteTool."""
    csv_file: str = Field(..., description="Path to the CSV file")
    db_name: str = Field(..., description="Name of the SQLite database")

class CSVToSQLiteTool(BaseTool):
    name: str = "CSV to SQLite"
    description: str = "Reads a clean CSV file and inserts CANDIDATE_NAME, EMAIL_ADDRESS, PHONE_NUMBER, LINKEDIN_ID, and SALARY_EXPECTANCY into an SQLite database table called INTERVIEW_SCHEDULED."
    args_schema: Type[BaseModel] = CSVToSQLiteInput

    def _run(self, csv_file: str, db_name: str) -> str:
        try:
            # Read the CSV directly
            df = pd.read_csv(csv_file)

            # Only required columns
            required_columns = ["CANDIDATE_NAME","INTERVIEW_DATE",
                "INTERVIEW_TIME", "EMAIL_ADDRESS", "PHONE_NUMBER", "LINKEDIN_ID", "SALARY_EXPECTANCY"]
            df = df[required_columns]

            # Drop rows with missing CANDIDATE_NAME
            df = df.dropna(subset=["CANDIDATE_NAME"])

            # Connect to SQLite and create table
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS INTERVIEW_SCHEDULED")

            create_table_query = """
            CREATE TABLE INTERVIEW_SCHEDULED (
                CANDIDATE_NAME TEXT,
                INTERVIEW_DATE TEXT,
                INTERVIEW_TIME TEXT,
                EMAIL_ADDRESS TEXT,
                PHONE_NUMBER TEXT,
                LINKEDIN_ID TEXT,
                SALARY_EXPECTANCY TEXT
            );
            """
            cursor.execute(create_table_query)

            # Insert into table
            df.to_sql('INTERVIEW_SCHEDULED', conn, if_exists='append', index=False)

            conn.commit()
            conn.close()
            return "Data successfully inserted into INTERVIEW_SCHEDULED table with selected columns."
        except Exception as e:
            return f"Error: {str(e)}"