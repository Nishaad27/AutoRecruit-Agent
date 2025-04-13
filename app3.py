import streamlit as st
import pandas as pd
import PyPDF2
from crewai import Crew
from agents import  resume_matcher, csv_writer_match, match_score_reader, resume_fetcher, shortlisted_writer, csv_to_sqlite_agent
from tasks import  match_task, save_match_task, filter_task, fetch_resume_task, save_shortlisted_task, db_insertion_task
from recruitment_automation import RecruitmentAutomation
from interview_scheduler_crew import SheetAutomation
from gmail_automation_new import GmailAutomation
import sqlite3
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
import time
st.set_page_config(page_title="Talent Acquisition AI", page_icon="🤖", layout="centered")
# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# Apply custom CSS
st.markdown("""
    <style>
        /* Global Styles */
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
        }
        /* Title Styling */
        .title {
            color: #1E88E5;
            font-size: 32px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }
        /* File Uploader */
        .stFileUploader {
            border: 2px dashed #1E88E5 !important;
            border-radius: 10px;
            padding: 10px;
        }
        /* Custom Button */
        .stButton>button {
            background: linear-gradient(90deg, #1E88E5, #42A5F5);
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #0D47A1, #1E88E5);
            transform: scale(1.05);
        }
        /* Chat Styling */
        .chat-box {
            border: 2px solid #42A5F5;
            background-color: #E3F2FD;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        /* Success Message */
        .stSuccess {
            background-color: #4CAF50 !important;
            color: white !important;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)
#resumes_dir_pdf = "./RESUMES"
resumes_dir_pdf = "./RESUMES_NEW"
resume_files_pdf = [os.path.join(resumes_dir_pdf, f) for f in os.listdir(resumes_dir_pdf) if f.endswith(".pdf")]

recruitment_system = RecruitmentAutomation()
# Define Crew
crew = Crew(
    agents=[ resume_matcher, csv_writer_match, match_score_reader, resume_fetcher, shortlisted_writer, csv_to_sqlite_agent],
    tasks=[ match_task, save_match_task, filter_task, fetch_resume_task, save_shortlisted_task, db_insertion_task],
)

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() or "" for page in pdf_reader.pages])
    return text.strip()

# Streamlit UI


st.markdown('<h1 class="title">🚀 Intelligent Talent Acquisition Assistant</h1>', unsafe_allow_html=True)
st.markdown("### **📂 Upload a Job Description & Find the Best Matches**")
st.divider()

# Upload Section
uploaded_file = st.file_uploader("📂 Upload Job Description (PDF)", type=["pdf"])
threshold = st.slider("🎯 Set Match Threshold", min_value=0, max_value=100, value=60, step=5)

# Initialize session state
if "matching_complete" not in st.session_state:
    st.session_state.matching_complete = False

if uploaded_file is not None:
    JD_text = extract_text_from_pdf(uploaded_file)
    st.text_area("📜 Extracted Job Description", JD_text, height=200, disabled=True)
    
    if st.button("🔍 Start Matching Process", use_container_width=True):
        with st.status("⏳ AI Matching in Progress...", expanded=True) as status:
            files_to_delete = [
    "applicant_resumes.csv",
    "resume_match_scores.csv",
    "shortlisted_candidates.csv"
   # "shortlisted_candidates.db"
]


            for file in files_to_delete:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted: {file}")
                else:
                    print(f"File not found, skipping: {file}")
            time.sleep(2)  # Simulate loading effect
            recruitment_system.kickoff(resume_files_pdf)
            time.sleep(5)
            crew.kickoff(inputs={'JD': JD_text, 'threshold': threshold})

            status.update(label="✅ Matching Completed!", state="complete")
            st.session_state.matching_complete = True  # Enable chat interface
            st.success("🎉 Candidates matched successfully!")

    # Show chat interface only after successful matching
    if st.session_state.matching_complete:
        st.divider()
        st.markdown('<h2 class="title">💬 Chat with Shortlisted Candidates Database</h2>', unsafe_allow_html=True)

        llm = ChatGroq(groq_api_key=groq_api_key, model="Llama3-8b-8192")
        conn = sqlite3.connect("shortlisted_candidates.db")

        cursor = conn.cursor()
         
        schema = """
    CREATE TABLE SHORTLISTED_CANDIDATES (
        NAME TEXT,
        MATCH_PERCENTAGE NUMERIC,
        EMAIL_ADDRESS TEXT,
        RESUME_CONTENT TEXT
    );
"""

        interview_schema = """
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


        prompt = ChatPromptTemplate.from_template(
    """ 
    Based on the schemas of the databases provided:
    
    Shortlisted Candidates Schema:
    {schema}
    
    Interview Scheduled Schema:
    {interview_schema}
    
    And based on the user query:
    User Query:
    {query}
    
    Generate an SQL query that can be executed on a sqlite3 database.
    
     If the query asks about shortlisted candidates, use the Shortlisted Candidates table.
     If the query asks about interviews, scheduled interviews, or how many candidates have interviews scheduled, use the Interview Scheduled table.
     If the query mentions work experience, contacts, projects, or education, only return the `resume_content` column from the Shortlisted Candidates table.
    
     Do NOT return anything except the SQL query and DO NOT give  ''' or markdown formatting.
        Just give the SQL query, nothing else.
    """
)

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        output_prompt = ChatPromptTemplate.from_template(
    """ 
    Based on the schemas of the databases provided:
    Shortlisted Candidates Schema:
    {schema}
    
    Interview Scheduled Schema:
    {interview_schema}
    
    Based on the user query:
    User Query:
    {query}
    
    Based on the answer fetched from the SQL query (which may contain resume content or interview details):
    Answer:
    {ans}
    
    If the query is related to skills, work experience, or projects, extract only the relevant information from the Answer (as it contains the full resume content) and ignore the database schema.
    If the query is related to scheduled interviews, extract only the relevant interview details.

    Provide the final output in a properly formatted and organized manner.
    Just give the output, nothing else.
    """
)

        output_chain = output_prompt | llm | output_parser

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        user_query = st.chat_input(placeholder="🔎 Ask about shortlisted candidates...")

        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            sql_query = chain.invoke({"schema": schema,"interview_schema":interview_schema, "query": user_query})
            data = cursor.execute(sql_query).fetchall()

            response = output_chain.invoke({"query": user_query, "schema": schema,"interview_schema":interview_schema, "ans": str(data)})

            with st.chat_message("assistant"):
                st.markdown(f'<div class="chat-box">{response}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})

        cursor.close()
        conn.close()
        st.markdown("---")
        st.markdown("### 📧 Send Interview Emails to Shortlisted Candidates")

        interview_time = st.text_input("🕒 Enter Interview Time (e.g., Monday, April 7th at 11:00 AM IST)")

        if 'email_sent' not in st.session_state:
              st.session_state.email_sent = False

        #interview_time = st.text_input("Enter interview time")
        #JD_text = st.text_area("Paste Job Description Here")

        if interview_time:
           # if not st.session_state.email_sent:
                if st.button("📨 Send Emails", type="primary", use_container_width=True):
                    load_dotenv()
                    google_form = os.getenv("GOOGLE_FORM_LINK", "")
                    organization_name = "Nexus AI"

                    def extract_details():
                        names, emails = [], []
                        try:
                            conn = sqlite3.connect("shortlisted_candidates.db")
                            cursor = conn.cursor()
                            result = cursor.execute("SELECT NAME, EMAIL_ADDRESS FROM SHORTLISTED_CANDIDATES")
                            for row in result:
                                names.append(row[0])
                                emails.append(row[1])
                            conn.close()
                        except sqlite3.Error as e:
                            st.error(f"❌ SQLite error: {e}")
                        return names, emails

                    names, emails = extract_details()

                    if not emails:
                        st.error("⚠️ No candidates found to send emails to.")
                    else:
                        try:
                            gmail_automation = GmailAutomation()
                            result = gmail_automation.kickoff(
                                JD_text,
                                organization_name,
                                interview_time,
                                emails,
                                google_form
                            )
                            st.success("✅ Emails sent successfully!")
                            st.session_state.email_sent = True
                        except Exception as e:
                            st.error(f"❌ Failed to send emails: {e}")

        # Show the sheet crew button only after emails are sent
        if st.session_state.email_sent:
                if st.button("🧠 Run Sheet Automation Crew"):
                    try:
                        sheet_crew = SheetAutomation()
                        sheet_crew.run()
                        st.success("📊 Sheet automation crew executed successfully.")

                        df = pd.read_csv("output_files/google_sheet_data.csv")  # Replace with your actual file path
                        st.session_state["interview_df"] = df
                        st.session_state["csv_data"] = df.to_csv(index=False).encode('utf-8')

                    except Exception as e:
                        st.error(f"❌ Sheet crew failed: {e}")

# Show interview schedule and download if available
        if "interview_df" in st.session_state and "csv_data" in st.session_state:
            st.write("### Interview Schedule", st.session_state["interview_df"])

            st.download_button(
                label="📥 Download CSV",
                data=st.session_state["csv_data"],
                file_name='interview_schedule.csv',
                mime='text/csv'
            )