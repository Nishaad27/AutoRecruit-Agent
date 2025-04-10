from crewai import Agent, Task, Crew,LLM
import time
import os
from custom_tools_pdf import PDFReadTool
from custom_tools_csv_append import CSVAppendTool

import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model='gemini/gemini-1.5-flash',
    api_key=os.environ["GEMINI_API_KEY"]
)

class RecruitmentAutomation:
    def __init__(self):
        self.resume_reader = Agent(
            role="Resume Reader",
            backstory="Specializes in extracting text from resumes.",
            goal="Extract raw text from resume having the file path {file_path}, including the applicant's name.",
            tools=[PDFReadTool("{file_path}")],
            verbose=True,
            llm = llm
        )

        self.csv_writer = Agent(
            role="CSV Writer",
            backstory="Stores extracted resume content in CSV format.",
            goal="Save the applicant names and their full resume content into a CSV file.",
            tools=[CSVAppendTool()],
            verbose=True,
            llm=llm
        )

    def create_tasks(self, file_path):
        extract_task = Task(
            description=(
                "Extract raw textual content from the given resume file having file path  {file_path}. "
                "Ensure that all text, including the applicant's name, work experience, education, "
                "and other sections, is accurately retrieved without modification. "
                "Pass the extracted data to the CSV writer for storage."
            ),
             expected_output=(
            "A dictionary containing the applicant's name and raw resume text.\n"
            "Example:\n"
            "{\n"
            "    'name': 'John Doe', 'text': 'Software Engineer with 3+ years of experience...'\n"
            "}"
        ),
            agent=self.resume_reader,
            inputs={"file_path": file_path}
        )

        save_task = Task(
            description=(
                "Append the extracted applicant names and their full resume content to a CSV file "
                "named 'applicant_resumes.csv'. Ensure the data is formatted properly but remains "
                "unaltered. Maintain accuracy and structure while avoiding data loss."
            ),
            expected_output=(
            "A CSV file named 'applicant_resumes.csv' with structured data.\n"
            "Example:\n"
            "| Name          | Resume Content |\n"
            "|--------------|---------------|\n"
            "| John Doe     | Software Engineer with 3+ years of experience... |\n"
            "| Jane Smith   | Data Scientist with 4 years of experience... |\n"
            "\nFile Path: 'applicant_resumes.csv'"
        ),
            agent=self.csv_writer,
            context=[extract_task]
        )

        return extract_task, save_task

    def kickoff(self, resume_files):
        for file_path in resume_files:
            extract_task, save_task = self.create_tasks(file_path)
            crew = Crew(
                agents=[self.resume_reader, self.csv_writer],
                tasks=[extract_task, save_task]
            )
            crew.kickoff(inputs={"file_path": file_path})
            time.sleep(5)  # Adding delay to prevent race conditions

if __name__ == "__main__":
    resumes_dir_pdf = "./DUMMY_3"
    resume_files_pdf = [os.path.join(resumes_dir_pdf, f) for f in os.listdir(resumes_dir_pdf) if f.endswith(".pdf")]

    recruitment_system = RecruitmentAutomation()
    recruitment_system.kickoff(resume_files_pdf)
