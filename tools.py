import os
from crewai_tools import FileReadTool
from custom_tools_pdf import PDFReadTool
from dotenv import load_dotenv
load_dotenv()

# Directory containing text resumes
#resumes_dir = "./resumes"
#resumes_dir_pdf = "./DUMMY_3"
# Get all text resume file paths (without looping inside CrewAI)
#resume_files = [os.path.join(resumes_dir, f) for f in os.listdir(resumes_dir) if f.endswith(".txt")]
#resume_files_pdf = [os.path.join(resumes_dir_pdf, f) for f in os.listdir(resumes_dir_pdf) if f.endswith(".pdf")]
# File reading tool (reads all resumes)
#file_reader = FileReadTool(file_path=resume_files)
#from custom_tool_list_pdf import ListPDFsTool
#list_pdf_tool = ListPDFsTool(resumes_dir)
#pdf_file_reader = PDFReadTool(file_path=resume_files_pdf)

applicant_resume_reader = FileReadTool(file_path = 'applicant_resumes.csv')
resume_match_score_reader = FileReadTool(file_path="resume_match_scores.csv")

# File writing tool (CSV storage)
#file_writer = FileWriteTool(file_path="summarized_resumes.csv")