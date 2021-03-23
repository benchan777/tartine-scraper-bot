from bot.main import bot
from dotenv import load_dotenv
import os

load_dotenv()

bot.run(os.getenv('bot_token'))