import json
from datetime import datetime
from pymongo import MongoClient
from .message_formatter import format_history_for_storage
import os

class HistoryManager:
    def __init__(self, user_id, db_name=os.getenv("DB_NAME"), collection_name="conversations"):
        self.user_id = user_id
        self.db_name = db_name
        self.collection_name = collection_name
        self.current_conversation = None

        # Initialize MongoDB client and access collection
        self.client = MongoClient(os.getenv("MONGO_URI"))  # Change to your MongoDB URI if needed
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

        # Ensure a document for the user exists
        self.ensure_user_document()
        self.load_or_create_conversation()

    def ensure_user_document(self):
        """Ensure a document exists for the user in MongoDB"""
        if not self.collection.find_one({"user_id": self.user_id}):
            self.collection.insert_one({
                "user_id": self.user_id,
                "chats": []
            })

    def load_or_create_conversation(self):
        """Load existing conversation or create a new one if none exists"""
        user_data = self.collection.find_one({"user_id": self.user_id})
        if user_data and user_data["chats"]:
            self.current_conversation = user_data["chats"][-1]  # Get the last conversation
        else:
            self.start_new_conversation()

    def start_new_conversation(self):
        """Start a new conversation"""
        self.current_conversation = {
            "timestamp": datetime.now().isoformat(),
            "messages": []
        }
        self.collection.update_one(
            {"user_id": self.user_id},
            {"$push": {"chats": self.current_conversation}}
        )

    def add_message(self, message):
        """Add a new message to the current conversation"""
        if not self.current_conversation:
            self.load_or_create_conversation()

        # Format message if it's not already formatted
        if isinstance(message, dict) and "role" in message:
            formatted_message = message
        else:
            formatted_message = format_history_for_storage(message)

        # Add message to current conversation and update in MongoDB
        self.current_conversation["messages"].append(formatted_message)
        self.collection.update_one(
            {"user_id": self.user_id, "chats.timestamp": self.current_conversation["timestamp"]},
            {"$push": {"chats.$.messages": formatted_message}}
        )

    def get_current_messages(self):
        """Retrieve messages from the current conversation"""
        if not self.current_conversation:
            self.load_or_create_conversation()
        return self.current_conversation["messages"]

    def clear_current_conversation(self):
        """Clear only the current conversation and start a new one"""
        # Remove the last conversation from MongoDB
        self.collection.update_one(
            {"user_id": self.user_id},
            {"$pop": {"chats": 1}}  # Removes the last item in the chats array
        )
        self.start_new_conversation()  # Start a new conversation
