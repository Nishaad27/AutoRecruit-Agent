from typing import Any, Optional, Type, List, Dict
import csv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class CSVAppendToolSchema(BaseModel):
    """Input schema for CSVAppendTool."""
    file_path: str = Field(..., description="Full path to the CSV file where data should be appended")
    data: List[Dict[str, Any]] = Field(..., description="List of dictionaries to be appended to the CSV file")

class CSVAppendTool(BaseTool):
    """A tool for appending structured data to a CSV file.
    
    This tool appends rows to an existing CSV file while ensuring:
    1. Data format matches CSV columns
    2. No overwriting of existing data
    3. Handles missing or incorrect file paths

    Example Usage:
        >>> tool = CSVAppendTool(file_path="applicant_resumes.csv")
        >>> tool.run(data=[{"Name": "John Doe", "Resume Content": "Software Engineer with 3 years experience..."}])
    """

    name: str = "Append data to a CSV file"
    description: str = "Appends structured data (list of dictionaries) to an existing CSV file."
    args_schema: Type[BaseModel] = CSVAppendToolSchema
    file_path: Optional[str] = None

    def __init__(self, file_path: Optional[str] = None, **kwargs: Any) -> None:
        if file_path is not None:
            kwargs['description'] = f"Appends data to a CSV file. Default file: {file_path}. You can override it using 'file_path'."
        
        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(self, **kwargs: Any) -> str:
        file_path = kwargs.get("file_path", self.file_path)
        data = kwargs.get("data", [])

        if not file_path or not data:
            return "Error: Both 'file_path' and 'data' must be provided."

        try:
            # Check if file exists to determine if we need to write headers
            file_exists = False
            try:
                with open(file_path, "r") as f:
                    file_exists = True
            except FileNotFoundError:
                pass  # File does not exist yet, we will create it

            # Open file in append mode
            with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = data[0].keys()  # Extract keys from first dictionary as column names
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()  # Write headers only if file does not exist

                writer.writerows(data)  # Append data rows
                
            return f"Successfully appended {len(data)} records to {file_path}."

        except PermissionError:
            return f"Error: Permission denied for file: {file_path}"
        except Exception as e:
            return f"Error: Failed to append to CSV {file_path}. {str(e)}"
