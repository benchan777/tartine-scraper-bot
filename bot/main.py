from bot.models import Base, CountryLoaf
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

load_dotenv()

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all())
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
Session.configure(bind = engine)
db = Session()
from bot.functions import store_info_embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(pass_context = True)
async def test(ctx, *args):
    database_test = CountryLoaf(
        availability = ' '.join(args),
        time = '8:00pm'
    )
    db.add(database_test)
    db.commit()

    await ctx.send(db.query(CountryLoaf.availability).filter_by(time = '8:00pm').first()[0])

@bot.command()
async def selenium_test(ctx):
    driver = webdriver.Chrome(os.getenv('webdriver_path')) #Instantiate Chrome webdriver
    driver.get("https://guerrero.tartine.menu/pickup/") #Scrape Tartine Guerrero location's menu

    items = driver.find_elements_by_class_name('menu-item-heading') #Retrieves item name
    descriptions = driver.find_elements_by_class_name('menu-item-description') #Retrieves item description
    prices = driver.find_elements_by_class_name('pricecolor') #Retrieves item price

    #Jank way to find if each item is in stock. Check if 'Not Available' appears anywhere within the clickable box. If not, assume item is available
    stock = driver.find_elements_by_class_name('mb12m')

    #Keep track of which item we're on in list of items
    index = 0

    for item in items:
        #Attempt to find description of current item. Display N/A if it can't be found
        try:
            description = descriptions[index].text
        except:
            description = 'N/A'

        #Attempt to find price of current item. Display N/A if it can't be found
        try:
            price = prices[index].text
        except:
            price = 'N/A'

        #Check if the string 'Not Available exists in this element at current index. If not, assume item is available and set availability as 'Available'
        availability = 'Not Available' if 'Not Available' in stock[index].text else 'Available'

        embed = store_info_embed(
            item.text, 
            description, 
            price, 
            availability,
            0x00ff00 if availability == 'Available' else 0xff0000
            )

        await ctx.send(embed = embed)

        index += 1

    driver.close()