from typing import Any, Optional, Type
import PyPDF2
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PDFReadToolSchema(BaseModel):
    """Input schema for PDFReadTool."""
    file_path: str = Field(..., description="Full path to the PDF file to read")


class PDFReadTool(BaseTool):
    """A tool for reading text content from PDF files using PyPDF2.
    
    This tool extracts text from a given PDF file, supporting:
    1. File path provided at construction.
    2. File path provided at runtime.
    
    Example Usage:
        >>> tool = PDFReadTool(file_path="/path/to/file.pdf")
        >>> content = tool.run()  # Reads the provided PDF file
        >>> content = tool.run(file_path="/path/to/other.pdf")  # Reads another PDF file
    """

    name: str = "Read a PDF file's content"
    description: str = "Extracts text from a given PDF file. Provide 'file_path' as an argument."
    args_schema: Type[BaseModel] = PDFReadToolSchema
    file_path: Optional[str] = None

    def __init__(self, file_path: Optional[str] = None, **kwargs: Any) -> None:
        if file_path is not None:
            kwargs['description'] = f"Extracts text from a PDF file. Default file: {file_path}. You can override it using 'file_path'."
        
        super().__init__(**kwargs)
        self.file_path = file_path

    def _run(self, **kwargs: Any) -> str:
        file_path = kwargs.get("file_path", self.file_path)
        if file_path is None:
            return "Error: No file path provided. Please specify a file path."

        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
                
                return text.strip() if text.strip() else "Error: No extractable text found in the PDF."
        
        except FileNotFoundError:
            return f"Error: File not found at path: {file_path}"
        except PermissionError:
            return f"Error: Permission denied for file: {file_path}"
        except Exception as e:
            return f"Error: Failed to read PDF {file_path}. {str(e)}"
