import os

from dotenv import load_dotenv
from pymongo import MongoClient


# Load .env file
load_dotenv()


# MongoDB settings
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://127.0.0.1:27017"
)

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "CodeGuard"
)


# Connect to MongoDB
client = MongoClient(MONGODB_URI)

# Select CodeGuard database
db = client[DATABASE_NAME]


# Collections
users_collection = db["users"]
chats_collection = db["chats"]


# Test MongoDB connection
try:
    client.admin.command("ping")

    print("================================")
    print("MongoDB Connected Successfully!")
    print("Database:", DATABASE_NAME)
    print("================================")

except Exception as error:

    print("================================")
    print("MongoDB Connection Failed!")
    print("Error:", error)
    print("================================")