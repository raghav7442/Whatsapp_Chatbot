from langchain.prompts import PromptTemplate
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain.agents.agent_types import AgentType
import logging

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the custom prompt template
custom_prompt = '''You are a job-seeking website that holds all job openings in your knowledge base, including information about job URL, position name, vessel type, salary, joining date, and country. When a user asks for specific job openings, extract and return the relevant information in the following format:

    JOB Title: "{position_name}"
    you have to give only the asked jobs only do not give any thing else insted of jobs in csv also only give output in string formate
    
    If no matching records are found, return: "No matching jobs found for the specified criteria."
    make sure you are return the answer as string ,
    when you found any jobs always give the job link attached with the same entry 
    we will provide maximum 5 entries at a time and minimum one 
    ANSWER SHOULD BE IN MAXIMUM 1400 WORDS DO NOT GIVE ANSWER'S IN MORE THAN 1400 WORDS
    Here is the query:
    
    DO NOT GENERATE ANYTHING INSTED OF JOBS DO NOT RECOMMED 
    YOU ARE JUST CSV AGENT WHO ONLY GIVES JOBS WHICH ARE AVAIALABE IN CSV IF YOU NOT FOUND JUST RETURN "NO JOBS ARE AVAILABLE IN THIS CRITERIA" IF FOUND YOU WILL RETURN THE JOBS LIKE
    *Position Name*= position name,
    *Date Of Joining*= date of joining,
    *Contract Duration*= the contract duration,
    *Salary*= the salary,
    *Vessel Type*= The vessel type,
    *Job url*=job_url #one url only witout using [] and () brackets
    
    Only return the right information only do not give anything random. before returning any data from anywhere, you need to check it once before sending the data
    
    {query}
    AI Answer: String(answer) 
'''

def get_answer_from_csv(content):
    prompt_template = PromptTemplate(template=custom_prompt, input_variables=["query"])

    # Create the CSV agent
    csv_agent = create_csv_agent(
        llm=ChatOpenAI(temperature=0, model="gpt-4o", api_key=api_key),
        path="database/data.csv",  
        prompt_template=prompt_template,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        allow_dangerous_code=True,
        handle_parsing_errors=True  
    )

    # Invoke the agent with the query and return the result as a string
    final_answer = csv_agent.invoke(content)
    return str(final_answer['output'])
