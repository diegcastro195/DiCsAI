# REYPAS BOT - Configuration
# All secrets live in the .env file and are loaded here with python-dotenv.
import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file sitting next to this file

# Meta WhatsApp API
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# These numbers will receive the orders
CHEF_NUMBER = os.getenv("CHEF_NUMBER")
DELIVERY_NUMBER = os.getenv("DELIVERY_NUMBER")

# Groq AI
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# REYPAS Menu (data, not a secret - stays here)
MENU = {
    "1": {"name": "Arepa de Choclo", "price": 3500},
    "2": {"name": "Arepa de Queso", "price": 4000},
    "3": {"name": "Arepa Mixta", "price": 5000},
    "4": {"name": "Arepa con Hogao", "price": 4500},
    "5": {"name": "Bebida - Agua", "price": 1500},
}
