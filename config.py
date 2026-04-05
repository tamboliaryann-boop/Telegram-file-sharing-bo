import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID', '')

# File Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
SUPPORTED_FORMATS = ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'jpg', 'png', 'zip']
