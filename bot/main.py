from bot.models import Base, CountryLoaf
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import asyncio, discord, os, requests, re

load_dotenv()

#Allows function to keep track of stock availability. If a change is detected, actions can be taken.
country_loaf_stock = ' '

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all()) #Initialize Discord bot
engine = create_engine(os.getenv('database_key')) #Create SQLAlchemy engine
Base.metadata.create_all(engine) #Create database tables
Session = sessionmaker(engine) #Define Session class
Session.configure(bind = engine) #Connect Session class to the engine
db = Session() #Initialize Session class as db

#Configure options for Chrome webdriver
options = webdriver.ChromeOptions()
options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')

#Import functions after initializing everything to avoid circular import error
from bot.functions import store_info_embed, store_country_loaf_info, send_text

@bot.event
async def on_ready():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = 'for bread 🍞'))
    print(f"Logged in as {bot.user}")

@bot.command()
async def test(ctx):
    driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver with defined options
    driver.get("https://guerrero.tartine.menu/pickup/") #Scrape Tartine Guerrero location's menu

    thumbnail = driver.find_elements_by_xpath("//div[@class='w_front_img' and @style='height:100%;']")

    #What the hell is this even
    url = re.search('url\(\&quot\;(.*?)\&quot\;\)', thumbnail[0].get_attribute('innerHTML')).group(1)
    print(url)

@bot.command()
#Display tartine's entire menu with item status
async def menu(ctx):
    driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver with defined options
    driver.get("https://guerrero.tartine.menu/pickup/") #Scrape Tartine Guerrero location's menu

    items = driver.find_elements_by_xpath("//span[@class='menu-item-heading ng-binding']") #Retrieves item name
    descriptions = driver.find_elements_by_xpath("//div[@class='menu-item-description twoline-ellipsis ng-binding ng-scope']") #Retrieves item description
    prices = driver.find_elements_by_xpath("//div[@class='pricecolor price ng-binding ng-scope']") #Retrieves item price
    thumbnail = driver.find_elements_by_xpath("//div[@class='w_front_img' and @style='height:100%;']") #Retrieves style element that contains thumbnail url

    #Jank way to find if each item is in stock. Check if 'Not Available' appears anywhere within the clickable box. If not, assume item is available
    stock_status = driver.find_elements_by_xpath("//div[@class='mb12m ng-scope']") #Retrieves status of item's stock

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
        availability = 'Not Available' if 'Not Available' in stock_status[index].text else 'Available'

        try:
            stock_status_html = stock_status[index].get_attribute('innerHTML')
            image_html = driver.find_elements_by_xpath("//button[@class='panel flexrow ihover menu-item ada-menu-button']")

            try:
                image_check = re.search('\"h\_(.*?)pe\"', image_html[index].get_attribute('innerHTML')).group(1)
            except:
                url = 'https://i.imgur.com/bAnFQSY.jpg'

            if image_check in stock_status_html:
                url = re.search('url\(\&quot\;(.*?)\&quot\;\)', thumbnail[index].get_attribute('innerHTML')).group(1)
            else:
                url = 'https://i.imgur.com/bAnFQSY.jpg'

        except Exception as e:
            print(e)
            url = 'https://i.imgur.com/bAnFQSY.jpg'

        embed = store_info_embed(
            item.text, 
            description,
            url,
            price, 
            availability,
            0x00ff00 if availability == 'Available' else 0xff0000
            )

        await ctx.send(embed = embed)

        index += 1

    driver.close()

@bot.command()
#Check stock of Country Loaf every 60 seconds
async def country(ctx):
    while True:
        #Put entire function into try except because sometimes, something random fails which kills the loop
        try:
            driver = webdriver.Chrome(executable_path = os.getenv('webdriver_path'), options = options) #Instantiate Chrome webdriver with defined options
            driver.get("https://guerrero.tartine.menu/pickup/") #Scrape Tartine Guerrero location's menu

            items = driver.find_elements_by_xpath("//span[@class='menu-item-heading ng-binding']") #Retrieves item name
            descriptions = driver.find_elements_by_xpath("//div[@class='menu-item-description twoline-ellipsis ng-binding ng-scope']") #Retrieves item description
            prices = driver.find_elements_by_xpath("//div[@class='pricecolor price ng-binding ng-scope']") #Retrieves item price
            thumbnail = driver.find_elements_by_xpath("//div[@class='w_front_img' and @style='height:100%;']") #Retrieves style element that contains thumbnail url
            stock_status = driver.find_elements_by_xpath("//div[@class='mb12m ng-scope']") #Retrieves status of item's stock

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
                url = re.search('url\(\&quot\;(.*?)\&quot\;\)', thumbnail[0].get_attribute('innerHTML')).group(1)
            except:
                url = 'https://i.imgur.com/bAnFQSY.jpg'

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
                    # requests.post(f"https://maker.ifttt.com/trigger/green/with/key/{os.getenv('ifttt_key')}")
                    # print('Stock has changed to available. Setting light to green.')
                    send_text('available')
                    country_loaf_stock = availability
                    store_country_loaf_info(availability)


                #Change light color to red if stock changes from available to unavailable
                elif availability == 'Not Available':
                    # requests.post(f"https://maker.ifttt.com/trigger/red/with/key/{os.getenv('ifttt_key')}")
                    # print('Stock has changed to unavailable. Setting light to red.')
                    send_text('unavailable')
                    country_loaf_stock = availability
                    store_country_loaf_info(availability)

                #If availability is N/A, do nothing. Scraping probably failed for some reason
                else:
                    print('Availability N/A. Maybe scraping failed?')

            embed = store_info_embed(
                item,
                description,
                url,
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