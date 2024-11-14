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

@app.route('/chat', methods=['POST'])
def receive_message():
    try:
        # Get incoming message and sender ID from Twilio request
        user_message = request.form['Body']
        sender_id = request.form['From']
        logging.info("Received message from {}: {}".format(sender_id, user_message))
        
        # Initialize PropertyAssistant with sender_id as user_id
        property_assistant = PropertyAssistant(user_id=sender_id)
        conversation_handler = ConversationHandler(property_assistant)
        
        # Retrieve current conversation messages
        conversation_history = property_assistant.conversation_history

        # Get AI response via LLM using conversation history
        ai_response = conversation_handler.handle_conversation(user_message)

        # Update conversation history with the new message pair
        property_assistant.add_user_assistant_pair(user_message, ai_response)

        # Send the AI's response back to the user
        send_message(sender_id, ai_response)
        return 'Valid response', 200

    except Exception as e:
        logging.error("Error handling the message: {}".format(e))
        return 'Error processing request', 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=20000)
