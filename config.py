# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Settings:
#     TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
#     TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
#     TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
#     GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#     NGROK_URL = os.getenv("NGROK_URL") # Needed for Twilio webhooks

# settings = Settings()


import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    NGROK_URL = os.getenv("NGROK_URL")

settings = Settings()