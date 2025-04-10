from crewai import Task
from agents import resume_matcher,csv_writer_match,resume_fetcher,shortlisted_writer,match_score_reader,csv_to_sqlite_agent
from custom_tools_db import CSVToSQLiteTool
from agents import tool_db

# Task 1: Extract Resume Text



match_task = Task(
    description=(
        "For each applicant listed in 'applicant_resumes.csv':\n"
        "1. Extract and parse their resume to identify:\n"
        "   - Key skills\n"
        "   - Relevant work experience\n"
        "   - Educational background\n"
        "   - Industry/domain-specific terminology\n"
        "2. Compare each of these components against the provided job description (JD) using semantic and contextual analysis.\n"
        "3. Compute a relevance score (0–100) by applying the following weights:\n"
        "   - Skills: 40%\n"
        "   - Experience: 30%\n"
        "   - Education: 15%\n"
        "   - Domain alignment: 15%\n"
        "4. Output a JSON-style list where each entry includes:\n"
        "   - name: Full name of the applicant\n"
        "   - match_percentage: Integer from 0 to 100 reflecting the overall alignment with the JD"
    ),
    expected_output=(
        "A list of dictionaries with this structure only:\n"
        "[\n"
        "    {\"name\": \"John Doe\", \"match_percentage\": 86},\n"
        "    {\"name\": \"Jane Smith\", \"match_percentage\": 74}\n"
        "]"
    ),
    agent=resume_matcher
)

save_match_task = Task(
    description=(
        "Save the calculated match percentages into a CSV file named 'resume_match_scores.csv'. "
        "Ensure that each entry is properly formatted and stored for further analysis."
    ),
    expected_output=(
        "A CSV file named 'resume_match_scores.csv' with structured data.\n"
        "Example:\n"
        "| Name          | Match Percentage |\n"
        "|--------------|----------------|\n"
        "| John Doe     | 85              |\n"
        "| Jane Smith   | 72              |\n"
        "\nFile Path: 'resume_match_scores.csv'"
        "The Match Percentage values should be pure numbers not objects or Strings"
        "Do not add ```csv at the start and ``` at the end. "
        "And Do not Write a Python script in the csv file give a pure csv file"
        
    ),
    agent=csv_writer_match,
    context=[match_task],  # Depends on match calculations
    output_file="resume_match_scores.csv"
)

filter_task = Task(
    description=(
        "Read the match percentages from 'resume_match_scores.csv' and filter candidates based on the given threshold {threshold}.\n"
        "Only include candidates who have a match percentage greater than or equal to the threshold {threshold} provided.\n"
        "The threshold is set dynamically during the execution and should be considered while filtering.\n"
        "Ensure that the filtering logic is robust and correctly identifies eligible candidates."
    ),
    expected_output=(
        "A structured list of shortlisted candidates with their match percentage.\n"
        "Example Output:\n"
        "[\n"
        "  { 'name': 'John Doe', 'match_percentage': 85 }\n"
        "]\n"
        "Candidates below the threshold should be excluded from the shortlist."
    ),
    agent=match_score_reader
)

# Task 6: Fetch Full Resume for Shortlisted Candidates
fetch_resume_task = Task(
    description=(
        "Retrieve the full resume content for each shortlisted candidate from 'applicant_resumes.csv'.\n"
        "Match candidates using their names and extract their corresponding resume content.\n"
        "Ensure that the retrieved data is correctly mapped to each candidate and does not contain duplicates."
    ),
    expected_output=(
        "A list of shortlisted candidates with their full resume content.\n"
        "Example Output:\n"
        "[\n"
        "  { 'name': 'John Doe', 'match_percentage': 85, 'resume_content': 'Experienced ML Engineer with expertise in NLP, Python, and TensorFlow.' }\n"
        "]\n"
        "Ensure data integrity and avoid mismatches between names and resume content."
    ),
    agent=resume_fetcher,
    context=[filter_task]
)

# Task 7: Save Shortlisted Candidates to CSV
save_shortlisted_task = Task(
    description=(
        "Save shortlisted candidates into a CSV file named 'shortlisted_candidates.csv'.\n"
        "The file should contain the following four columns: NAME, MATCH_PERCENTAGE (Numeric), EMAIL_ADDRESS, and RESUME_CONTENT.\n"
        "Ensure that:\n"
        "  - MATCH_PERCENTAGE values are stored as numbers (not strings or percentage symbols).\n"
        "  - EMAIL_ADDRESS is accurately extracted using regex and matched correctly.\n"
        "  - RESUME_CONTENT is stored exactly as extracted, without any additional formatting or cleanup.\n"
        "  - Missing fields (if any) are stored as empty strings.\n"
        "  - The file structure remains consistent and does not contain any extra metadata or columns."
    ),
    expected_output=(
        "A CSV file named 'shortlisted_candidates.csv' with the following structure:\n"
        "| NAME       | MATCH_PERCENTAGE | EMAIL_ADDRESS     | RESUME_CONTENT                         |\n"
        "|------------|------------------|-------------------|----------------------------------------|\n"
        "| John Doe   | 85               | john@example.com  | Experienced ML Engineer with expertise... |\n"
        "\n"
        "File Path: 'shortlisted_candidates.csv'\n"
        "Ensure that numeric values remain in pure number format.\n"
        "Do NOT include Markdown code block markers like ```csv and ```.\n"
        "Strictly maintain these four columns in the CSV: NAME, MATCH_PERCENTAGE, EMAIL_ADDRESS, and RESUME_CONTENT."
    ),
    agent=shortlisted_writer,
    context=[fetch_resume_task],
    output_file="shortlisted_candidates.csv"
)


db_insertion_task = Task(
    description="Read the CSV file named 'shortlisted_candidates.csv', clean the data, and insert it into the SHORTLISTED_CANDIDATES table in SQLite. Ensure that only valid rows are inserted, and data integrity is maintained.",
    expected_output="The database should contain all valid rows from the CSV file without any empty or invalid data.",
    agent=csv_to_sqlite_agent,
    tools=[tool_db],
    parameters={"csv_file": "shortlisted_candidates.csv", "db_name": "shortlisted_candidates.db"}
)