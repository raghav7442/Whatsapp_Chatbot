from groq import Groq
from config.tools_config import TOOLS_CONFIG
from functions.backend import get_answer_from_csv
from utils.history_manager import HistoryManager
import os

class PropertyAssistant:
    def __init__(self, user_id):
        self._client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self._model = "llama-3.1-70b-versatile"
        self.name = "Property Recommender Chatbot"
        self._available_functions = {
            "get_answer_from_csv": get_answer_from_csv,
        }
        self._system_message = f"""
        here are availabe tools/ functions you have{self.available_functions}
        you are a job recommendation system you will help user with providing them the jobs with asking them some multiple questions 
        1. greet him and ask his name
        2. ask him about the what type of Position he want 
        3. Ask him about the vessel type 
        4. ask him about the expected salary for the particular position
        5. Ask him about the citizenship of him
       after getting all the requirements from user, you can use get_answer_from_csv tool for searching the actual jobs which is more precise to user
            
            - Example: {{"tool_name": "get_answer_from_csv", "tool_input":"Give me all in 1500 words maximum job details in this format:
            *JOB Title*: user anser-position
            *Vessel Type*: user answer -vessel_type
            *Date of Joining*: user answer -date_of_joining
            *Salary*: user-answer salary
           }} 
        
        you are a dedicated chatbot which recommed job positions in only vessels/ships with collaboration with balticshipping.com and you are fantastic chatbot with the ability to delever right information about the customer and all, 
        for example:
        user:hello 
        ai: hello to your job search portal, can i have your name?
        user: yes my name is xyz.
        ai:Nice to meet you xyz, What position are you looking for?
        user: i am looking for cheif engineer 
        ai: greate! What type of vessel are you interested in, XYZ?
        user:I am looking for General Cargo Vessel.
        ai: General Cargo vessel is good choise XYZ, What is your desired salary for this position?
        user: 6000 usd
        ai: nice lastly can i have your citizenship?
        user:I am Indian
        ai: {{"tool_name": "get_answer_from_csv", "tool_input": ive me all in 1500 words maximum job details in this format:
            *JOB Title*: cheif engineer
            *Vessel Type*: General Cargo Vessel
            *Date of Joining*: user answer -date_of_joining
            *Salary*: 6000 usd}}
        

        
        after giving job detils if user want more jobs ask him core questions like position, salary, vessel type
        or if user want to chat chat him like a good manager in professional way
        
        REMEMBER DO NOT ASK QUESTIONS MORE THATN 5 AS I MENTIOND, GIVE ANSWERS AFTER GETTING ALL THE DETAILS FROM THE USER, DO NOT CREATE ANY JOB OPENINGS FROM YOUR OWN,
        
        
        
        
        
        """
        self._history_manager = HistoryManager(user_id)

        # Start the conversation with a system message if it's a new conversation
        if not self._history_manager.get_current_messages():
            self._history_manager.add_message({
                "role": "system",
                "content": self._system_message
            })

    @property
    def client(self):
        return self._client

    @property
    def model(self):
        return self._model

    @property
    def available_functions(self):
        return self._available_functions

    @property
    def system_message(self):
        return self._system_message

    @property
    def conversation_history(self):
        return self._history_manager.get_current_messages()

    def get_all_tools(self):
        all_tools = []
        for tool_list in TOOLS_CONFIG.values():
            all_tools.extend(tool_list)
        return all_tools

    def add_to_history(self, message):
        """Add a message (user or assistant) to the conversation history."""
        self._history_manager.add_message(message)

    def add_user_assistant_pair(self, user_message, assistant_response):
        """Add a user and assistant message as a paired entry in the conversation history."""
        self._history_manager.add_user_assistant_pair(user_message, assistant_response)

    def clear_history(self):
        """Clear the conversation history and reset with the system message."""
        self._history_manager.clear_current_conversation()
        self._history_manager.add_message({
            "role": "system",
            "content": self._system_message
        })