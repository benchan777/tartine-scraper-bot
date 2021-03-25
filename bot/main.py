from bot.models import Base, CountryLoaf
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import asyncio, discord, os, requests

load_dotenv()

#Allows function to keep track of stock availability. If a change is detected, actions can be taken.
country_loaf_stock = ' '

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all()) #Initialize Discord bot
engine = create_engine('sqlite:///database.db') #Create SQLAlchemy engine
Base.metadata.create_all(engine) #Create database tables
Session = sessionmaker(engine) #Define Session class
Session.configure(bind = engine) #Connect Session class to the engine
db = Session() #Initialize Session class as db

#Configure options for Chrome webdriver
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')

#Import functions after initializing everything to avoid circular import error
from bot.functions import store_info_embed, store_country_loaf_info

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Game(name = 'Looking for bread'))
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
    driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver with defined options
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

        #Put entire function into try except because sometimes, something random fails which kills the loop
        try:
            driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver with defined options
            driver.get("https://guerrero.tartine.menu/pickup/") #Scrape Tartine Guerrero location's menu

            items = driver.find_elements_by_class_name('menu-item-heading') #Retrieves item name
            descriptions = driver.find_elements_by_class_name('menu-item-description') #Retrieves item description
            prices = driver.find_elements_by_class_name('pricecolor') #Retrieves item price
            stock_status = driver.find_elements_by_class_name('mb12m') #Retrieves status of item's stock

            #Country loaf is the first item on the menu. Index 0 will retrieve all information about Country loaf
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

            #Checks status of bread stock from previous scrape. If there is a change, trigger a change in light color
            global country_loaf_stock
            if availability != country_loaf_stock:
                #Change light color to green if stock changes from unavailable to available
                if availability == 'Available':
                    requests.post(f"https://maker.ifttt.com/trigger/green/with/key/{os.getenv('ifttt_key')}")
                    print('Stock has changed to available. Setting light to green.')
                    country_loaf_stock = availability

                #Change light color to red if stock changes from available to unavailable
                elif availability == 'Not Available':
                    requests.post(f"https://maker.ifttt.com/trigger/red/with/key/{os.getenv('ifttt_key')}")
                    print('Stock has changed to unavailable. Setting light to red.')
                    country_loaf_stock = availability

                #If availability is N/A, do nothing. Scraping probably failed for some reason
                else:
                    print('Availability N/A. Maybe scraping failed?')

            store_country_loaf_info(availability)

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

        except Exception as e:
            print(e)
            pass