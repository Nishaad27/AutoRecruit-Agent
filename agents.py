from crewai import Agent, LLM
from tools import applicant_resume_reader,resume_match_score_reader
from custom_tools_db import CSVToSQLiteTool

from custom_tools_pdf import PDFReadTool
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model='gemini/gemini-1.5-flash',
    api_key=os.environ["GEMINI_API_KEY"]
)




resume_matcher = Agent(
    role="Resume Matcher",
    backstory=(
        "Sophia Hayes is an experienced recruitment analyst specializing in AI-powered "
        "resume matching. With expertise in NLP and candidate evaluation, she ensures that "
        "applicant resumes are accurately compared with job descriptions {JD} to determine relevance."
    ),
    goal="Analyze resumes from 'applicant_resumes.csv' and compute match percentages against the given job description.",
    llm=llm,
    tools = [applicant_resume_reader],
    verbose=True
)

csv_writer_match = Agent(
    role="Match Score Writer",
    backstory=(
        "Liam Parker is a data specialist who ensures structured storage of candidate-job match scores. "
        "His expertise lies in formatting and preserving information for easy retrieval."
    ),
    goal="Store applicant names and their JD match percentage into 'resume_match_scores.csv'.",
    llm=llm,
    verbose=True
)


match_score_reader = Agent(
    role="Match Score Reader",
    backstory="Emma Collins is a data analyst who filters candidates based on match percentage.",
    goal="Read 'resume_match_scores.csv' and shortlist candidates above the given threshold {threshold}.",
    tools=[resume_match_score_reader],
    llm=llm,
    verbose=True
)

resume_fetcher = Agent(
    role="Resume Fetcher",
    backstory="David Carter retrieves resumes of shortlisted candidates from 'applicant_resumes.csv'.",
    goal="Fetch full resume content for shortlisted candidates based on their names.",
    llm=llm,
    tools = [applicant_resume_reader],
    verbose=True
)

shortlisted_writer = Agent(
    role="Shortlisted Candidates Writer",
    backstory="Sophia Brown ensures that shortlisted candidates are properly stored in a structured CSV format.",
    goal="Write shortlisted candidates' names, match percentage, and resume content into 'shortlisted_candidates.csv'.",
    llm=llm,
    verbose=True
)
csv_to_sqlite_agent = Agent(
    name="CSV Database Inserter",
    role="Data Manager",
    goal="Read a CSV file and insert its contents into an SQLite database.",
    backstory="You are a highly efficient data manager responsible for ensuring that candidate data is properly stored in the database.",
    tools=[CSVToSQLiteTool()],
    verbose=True
)