from crewai import Agent, LLM
from tools import applicant_resume_reader,resume_match_score_reader
from custom_tools_db_new import CSVToSQLiteTool
tool_db = CSVToSQLiteTool(file_path="shortlisted_candidates.csv")
from custom_tools_pdf import PDFReadTool
import os
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model='gemini/gemini-1.5-flash',
    api_key=os.environ["GEMINI_API_KEY"]
)




resume_matcher = Agent(
    role="Resume Relevance Evaluator",
    backstory=(
        "Sophia Hayes is an expert AI-powered recruitment analyst with deep knowledge in semantic matching, talent acquisition, "
        "and contextual document understanding. She specializes in interpreting resumes in natural language and making precise, "
        "human-like judgments about their relevance to job descriptions (JDs). Rather than relying on simple keyword overlap, "
        "Sophia leverages nuanced semantic reasoning, industry context, and evaluative heuristics to determine the strength of fit "
        "between a candidate and a given role."
    ),
    goal=(
        "Assess each applicant's resume from 'applicant_resumes.csv' against the provided JD using semantic analysis. "
        "Determine an overall match percentage (0–100) that reflects alignment across four key dimensions:\n"
        "- Skills (40% weight)\n"
        "- Experience (30% weight)\n"
        "- Education (15% weight)\n"
        "- Domain alignment (15% weight)\n"
        "Scores must be based on meaning and context rather than keyword count, ensuring fair and insightful evaluation."
    ),
    llm=llm,
    tools=[applicant_resume_reader],
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
    goal="Write shortlisted candidates' names, match percentage, email address, and resume content into 'shortlisted_candidates.csv'.",
    llm=llm,
    verbose=True
)

csv_to_sqlite_agent = Agent(
    name="CSV Database Inserter",
    role="Data Manager",
    goal="Read a CSV file and insert its contents into an SQLite database.",
    backstory="You are a highly efficient data manager responsible for ensuring that candidate data is properly stored in the database.",
    tools=[tool_db],
    verbose=True
)