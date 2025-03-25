from crewai import Crew
from agents import resume_matcher,csv_writer_match,match_score_reader,resume_fetcher,shortlisted_writer,csv_to_sqlite_agent
from tasks import match_task,save_match_task,filter_task,fetch_resume_task,save_shortlisted_task,db_insertion_task
from recruitment_automation import RecruitmentAutomation
import os

# Define the crew with only the necessary agents and tasks
resumes_dir_pdf = "RESUMES"
resume_files_pdf = [os.path.join(resumes_dir_pdf, f) for f in os.listdir(resumes_dir_pdf) if f.endswith(".pdf")]

recruitment_system = RecruitmentAutomation()


crew = Crew(
        agents=[
             resume_matcher, csv_writer_match,
            match_score_reader, resume_fetcher, shortlisted_writer,csv_to_sqlite_agent
        ],
        tasks=[
             match_task, save_match_task,
            filter_task, fetch_resume_task, save_shortlisted_task,db_insertion_task
        ],
    )
# Run the process
JD = ""
with open("JD.txt",'r') as f:
    JD = f.read()
threshhold = 60
if __name__ == "__main__":
    #recruitment_system.kickoff(resume_files_pdf)
    crew.kickoff(inputs={'JD':JD,
                         'threshold':threshhold})
