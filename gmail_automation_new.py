import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from gmail_tool_new import GmailTool

# Load environment variables
load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize LLM
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=gemini_api_key
)

gmail_tool = GmailTool()

class GmailAutomation:
    def __init__(self):
        self.mail_composer_agent = Agent(
         role="Outreach Email Composing Agent",
        goal="Draft a warm and professional outreach email in markdown format to inform a potential candidate that they’ve been identified as a good fit and are invited for an interview if interested.",
        backstory="You are an HR assistant responsible for composing initial outreach emails to candidates who haven’t applied directly but were found through job portals and internal systems. The goal is to inform them about a relevant opportunity and invite them to express interest by filling a provided form or replying.",
        llm=llm,
        allow_delegation=False,
        verbose=True
      )


        self.mail_sender_agent = Agent(
            role="Interview Email Sending Agent",
            goal="Send the interview email composed by the previous agent to the candidate using GmailTool.",
            backstory="You are an automated Gmail agent. You send interview emails to candidates having the email address {receiver_emails} based on the markdown input provided.",
            llm=llm,
            tools=[gmail_tool],
            allow_delegation=False,
            verbose=True
        )

    def create_task(self, job_description, organization_name, interview_time, receiver_emails, google_form):
        # Email Composition Task
        
        self.mail_composer_task = Task(
        name="mail_composer_task",
        description=(
        f"You are reaching out to a potential candidate ,(note that just start the email by Dear candidate) who has not applied directly, "
        f"Do not give an example name, but just write that on belahf of the team of {organization_name} you are reaching out to the candidate. "
        f"but was identified as a strong match for a role at **{organization_name}** based on their skills and experience. "
        f"Please compose a **professional, warm, and inviting** email in **markdown format**.\n\n"
        f"Use the following job description for context:\n\n{job_description}\n\n"
        f"The interview is tentatively scheduled for **{interview_time}**.\n"
        f"{'Include this Google Form link in the email: ' + google_form if google_form else ''}\n\n"
        f"Clearly mention that if the candidate is interested, they can fill out the form to proceed with scheduling the interview. "
        f"Make sure the tone is respectful, engaging, and gives them the option to ignore if they are not looking for opportunities currently."
    ),
    expected_output="Interview outreach email in markdown format",
    agent=self.mail_composer_agent
)


        # Email Sending Task - will receive markdown output of previous task as body
        self.mail_sender_task = Task(
            description="Send the composed interview invitation email to the candidate having the email address {receiver_emails} using GmailTool. Use the markdown output as the email body.",
            expected_output="Email sent to candidate",
            tools=[gmail_tool],
            agent=self.mail_sender_agent,
            input={"receiver_emails": receiver_emails}
        )

        return self.mail_composer_task, self.mail_sender_task

    def kickoff(self, job_description ,organization_name, interview_time, receiver_emails,google_form):
        self.mail_composer_task, self.mail_sender_task = self.create_task(
            job_description, organization_name, interview_time, receiver_emails,google_form
        )
        crew = Crew(
            tasks=[self.mail_composer_task, self.mail_sender_task],
            llm=llm,
            verbose=True,
            context = {'receiver_emails' : receiver_emails},
            process_flow="sequential"  # Ensure tasks are executed in order
        )
        result = crew.kickoff({
            'job_description': job_description,
            
            'organization_name': organization_name,
            'interview_time': interview_time,
            'receiver_emails': receiver_emails,
            'google_form' : google_form
        })
        return result


if __name__ == '__main__':
    job_description = "We are hiring a Machine Learning Engineer with experience in Python, TensorFlow, and LLMs. Strong problem-solving skills and knowledge of generative AI are a plus."
    organization_name = "OpenAI Talent Team"
    interview_time = "Monday, April 7th at 11:00 AM IST"
    receiver_emails = ["nishaad.may.27@gmail.com"]
    google_form = "https://forms.gle/exampleform"

    gmail_automation = GmailAutomation()
    result = gmail_automation.kickoff(job_description, organization_name, interview_time, receiver_emails,google_form)
    print(result)
