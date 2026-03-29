import os
import ast
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
ADMIN_IDS = ast.literal_eval(os.getenv('ADMIN_IDS', '[]'))

DATABASE_PATH = 'production_database.db'

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(CURR_DIR, 'logs')
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), 'uploads')

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)