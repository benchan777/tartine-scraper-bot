from bot.main import db
from bot.models import CountryLoaf
import datetime, discord, pytz, smtplib, ssl, os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

#Function that helps to create discord embeds for item info
def store_info_embed(name, description, thumbnail, price, availability, color):
    embed_1 = 'Error' if len(str(name)) == 0 else name
    embed_2 = 'Error' if len(str(description)) == 0 else description
    embed_3 = 0xffff00 if len(str(color)) == 0 else color
    embed_4 = 'Error' if len(str(price)) == 0 else price
    embed_5 = 'Error' if len(str(availability)) == 0 else availability

    embed = discord.Embed(title = embed_1, description = embed_2, color = embed_3)
    embed.set_thumbnail(url = thumbnail)

    embed.add_field(name = 'Price', value = price, inline = True)
    embed.add_field(name = 'Availability', value = availability, inline = True)

    return embed

#Stores date/time/availability info of country loaf every time site is scraped
def store_country_loaf_info(availability):
    PDT = pytz.timezone('America/Los_Angeles') #Get PDT timezone
    now = datetime.datetime.now(PDT)

    new_entry = CountryLoaf(
        datetime = now,
        date = now.strftime("%m/%d/%Y"),
        time = now.strftime("%H:%M:%S"),
        availability = availability
    )
    db.add(new_entry)
    db.commit()

def send_text(availability):
    if availability == 'available':
        message = f"""From: {os.getenv('email')}\nTo: {os.getenv('receiver_email')}\nSubject: Country loaf in stock!\n
        
Country loaf is now in stock!\n
Order here: https://guerrero.tartine.menu/pickup/"""

    else:
        message = f"""From: {os.getenv('email')}\nTo: {os.getenv('receiver_email')}\nSubject: Country loaf out of stock.\n
        
Country loaf is now out of stock.\n
We will notify you when stock is replenished."""

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as server:
        server.login(os.getenv('email'), os.getenv('password'))
        server.sendmail(os.getenv('email'), os.getenv('receiver_email'), message)