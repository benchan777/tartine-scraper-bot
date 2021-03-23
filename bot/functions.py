import discord
from discord.ext import commands

#Function that helps to create discord embeds for item info
def store_info_embed(name, description, price, availability, color):
    embed_1 = 'Error' if len(str(name)) == 0 else name
    embed_2 = 'Error' if len(str(description)) == 0 else description
    embed_3 = 0xffff00 if len(str(color)) == 0 else color
    embed_4 = 'Error' if len(str(price)) == 0 else price
    embed_5 = 'Error' if len(str(availability)) == 0 else availability

    embed = discord.Embed(title = embed_1, description = embed_2, color = embed_3)
    # embed.set_thumbnail(url = thumbnail)

    embed.add_field(name = 'Price', value = price, inline = True)
    embed.add_field(name = 'Availability', value = availability, inline = True)

    return embed