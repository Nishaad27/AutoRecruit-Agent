import sqlite3
import time
from crewai import Crew
from agents import resume_matcher,csv_writer_match,match_score_reader,resume_fetcher,shortlisted_writer,csv_to_sqlite_agent
from tasks import match_task,save_match_task,filter_task,fetch_resume_task,save_shortlisted_task,db_insertion_task
from recruitment_automation import RecruitmentAutomation
from gmail_automation_new import GmailAutomation
import os


def extract_details():
    names = []
    emails = []
    db_name = "shortlisted_candidates.db"  # <-- Replace with your actual DB name

    try:
    # Connect to SQLite DB
        conn = sqlite3.connect(db_name)

    # Query the table
        query = "SELECT NAME,EMAIL_ADDRESS FROM SHORTLISTED_CANDIDATES"
   # df = pd.read_sql_query(query, conn)
        cursor = conn.cursor()
        result =  cursor.execute(query)

    
    #print(df)
        for row in result:
            names.append(row[0])
            emails.append(row[1])


        conn.close()

    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    return names, emails


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
    #crew.kickoff(inputs={'JD':JD,
                        #'threshold':threshhold})
    names, emails = extract_details()
    
        
    job_description = JD
        
    organization_name = "OpenAI Talent Team"
    interview_time = "Monday, April 7th at 11:00 AM IST"
    candidate_email = ["mayurakshipani84@gmail.com","nishaad.may.27@gmail.com"]
    google_form = "https://forms.gle/exampleform"
    gmail_automation = GmailAutomation()
       
    result = gmail_automation.kickoff(job_description, organization_name, interview_time, candidate_email,google_form)
    print(result)


