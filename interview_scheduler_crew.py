from crewai import Agent, Task, LLM, Crew
import os
from google_sheets_tool_new import GoogleSheetsTool  # Assuming you have your tool defined as mentioned earlier
from crewai_tools import FileReadTool  # Assuming you have a file read tool defined
file_read_tool = FileReadTool(file_path='output_files/google_sheet_data.csv')  # Replace with your actual file path
# Set up the tool
from custom_tools_db_scheduled import CSVToSQLiteTool
tool_db = CSVToSQLiteTool(file_path="shortlisted_candidates.db",db_name="shortlisted_candidates.db")
sheet_tool = GoogleSheetsTool()

# Set up the Gemini API key for the LLM
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize the LLM with Gemini API
llm = LLM(model="gemini/gemini-1.5-flash", api_key=gemini_api_key)

# Agent 1: Fetch Google Sheets Data and Save as CSV
agent_fetch = Agent(
    role="Google Sheets Data Fetcher",
    goal="Fetch data from Google Sheets and save it as a CSV file.",
    backstory="An agent that fetches data from a specified Google Sheet and saves it as a CSV file using the tool.",
    tools=[sheet_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)


task_fetch = Task(
    description="Fetch the Google Sheet data using the tool and save it as a CSV file.",
    expected_output="A confirmation message with the CSV file path.",
    agent=agent_fetch,
    tools=[sheet_tool],
     
)
csv_to_sqlite_agent_2 = Agent(
    name="CSV Database Inserter",
    role="Data Manager",
    goal="Read a CSV file and insert its contents into an SQLite database(shortlisted_candidates.db).",
    backstory="You are a highly efficient data manager responsible for ensuring that candidate data is properly stored in the database.",
    tools=[tool_db],
    verbose=True
)
db_insertion_task_2 = Task(
    description="Read the CSV file named 'output_files/google_sheet_data.csv' and insert its contents into the INTERVIEW_SCHEDULED table in the shortlisted_candidates.db database.",
    expected_output="The database should contain all rows from the CSV file.",
    agent=csv_to_sqlite_agent_2,
    tools=[tool_db],
    parameters={"csv_file": "output_files/google_sheet_data.csv", "db_name": "shortlisted_candidates.db"}
)

class SheetAutomation:
    def __init__(self):
        self.sheet_fetcher_agent = agent_fetch
        self.sheet_fetcher_task = task_fetch
        self.csv_to_sqlite_agent = csv_to_sqlite_agent_2
        self.db_insertion_task = db_insertion_task_2

    def run(self):
        crew = Crew(agents=[self.sheet_fetcher_agent,self.csv_to_sqlite_agent], tasks=[self.sheet_fetcher_task,self.db_insertion_task])
        crew.kickoff()


if __name__ == "__main__":
    sheet_automation = SheetAutomation()
    sheet_automation.run()