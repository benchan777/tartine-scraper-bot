from bot.models import Base, CountryLoaf
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import discord
from discord.ext import commands, tasks
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import asyncio
import requests

load_dotenv()
country_loaf_stock = 'Not Available'

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all())
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
Session.configure(bind = engine)
db = Session()

options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')

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
    driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver
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

@bot.command()
#Test function to check stock of Country Loaf every 60 seconds
async def track_country_loaf(ctx):
    while True:
        driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options)
        driver.get("https://guerrero.tartine.menu/pickup/")

        items = driver.find_elements_by_class_name('menu-item-heading')
        descriptions = driver.find_elements_by_class_name('menu-item-description')
        prices = driver.find_elements_by_class_name('pricecolor')
        stock_status = driver.find_elements_by_class_name('mb12m')

        try:
            item = items[0].text
        except:
            item = 'N/A'

        try:
            description = descriptions[0].text
        except:
            description = 'N/A'

        try:
            price = prices[0].text
        except:
            price = 'N/A'

        try:
            stock = stock_status[0].text
        except:
            stock = 'N/A'

        availability = 'Not Available' if 'Not Available' in stock else 'N/A' if 'N/A' in stock else 'Available'

        global country_loaf_stock
        if availability != country_loaf_stock:
            if availability == 'Available':
                requests.post(f"https://maker.ifttt.com/trigger/green/with/key/{os.getenv('ifttt_key')}")
                print('Stock has changed to available. Setting light to green.')
                country_loaf_stock = availability
            elif availability == 'Not Available':
                requests.post(f"https://maker.ifttt.com/trigger/red/with/key/{os.getenv('ifttt_key')}")
                print('Stock has changed to unavailable. Setting light to red.')
                country_loaf_stock = availability
            else:
                print('Availability N/A. Maybe scraping failed?')

        embed = store_info_embed(
            item,
            description,
            price,
            availability,
            0x00ff00 if availability == 'Available' else 0xff0000 if availability == 'Not Available' else 0xffff00
        )

        await ctx.send(embed = embed)
        driver.close()
        await asyncio.sleep(60)