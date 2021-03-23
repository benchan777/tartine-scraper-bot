from bot.models import BreadStock
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands
import os

load_dotenv()

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all())
engine = create_engine('sqlite:///database.db')
Base.metadata.creat_all(engine)
Session = sessionmaker(engine)
Session.configure(bind = engine)
db = Session()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")