from database import client, db


try:
    client.admin.command("ping")

    print("MongoDB connected successfully!")
    print("Database:", db.name)

except Exception as error:

    print("MongoDB connection failed!")
    print("Error:", error)