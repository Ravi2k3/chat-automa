import sys
import os
from dotenv import load_dotenv

# Add the path of your application to the PYTHONPATH
sys.path.insert(0, "/home/ecstra/Automa/Interactive_Learning")

# Load environment variables from .env file
load_dotenv("/home/ecstra/Automa/Interactive_Learning/.env")

from chat_system import app as application