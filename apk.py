from flask import Flask, request
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from core.assistant import PropertyAssistant
from core.conversation import ConversationHandler
from utils.twilio_api import send_message  
import logging
from utils.history_manager import HistoryManager  

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
logging.basicConfig(level=logging.INFO)

# MongoDB setup
mongo_client = MongoClient(os.getenv('MONGODB_URI'))
db = mongo_client[os.getenv("DB_NAME")]
chats_collection = db[os.getenv("COLLECTION_NAME")]

# Initialize the assistant
property_assistant = PropertyAssistant()
conversation_handler = ConversationHandler(property_assistant)

@app.route('/chat', methods=['POST'])
def receive_message():
    try:
        # Get incoming message and sender ID from Twilio request
        user_message = request.form['Body']
        sender_id = request.form['From']
        logging.info("Received message from {}: {}".format(sender_id, user_message))
        
        # Initialize HistoryManager for the user
        history_manager = HistoryManager(sender_id)
        
        # Retrieve current conversation messages
        conversation_history = history_manager.get_current_messages()

        # Get AI response via LLM using conversation history
        ai_response = conversation_handler.handle_conversation(user_message)

        # Update conversation history with the new message pair
        history_manager.add_user_assistant_pair(user_message, ai_response)

        # Send the AI's response back to the user
        send_message(sender_id, ai_response)
        return 'Valid response', 200

    except Exception as e:
        logging.error("Error handling the message: {}".format(e))
        return 'Error processing request', 500

if __name__ == '__main__':
    app.run(debug=False, port=20000)
