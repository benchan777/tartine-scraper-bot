# Tartine Scraper Bot
A bot that continually scrapes tartine's website with Selenium for bread availability because the bread is out of stock every time I decide I want to order some. Uses IFTTT and Kasa integration to change color light bulb to red/green on availability status change. Also utilizes SMTP and SMS gateway in order to notify specified users of bread availability via text message.

## Invite Bot
[Click here to invite bot to your server](https://discord.com/api/oauth2/authorize?client_id=823827148439420939&permissions=0&scope=bot)

## Running the bot locally
1. Go to the Developer portal [here](https://discord.com/developers/applications) to create a new bot and retrieve its token.

1. Clone the repo:
`git clone https://github.com/benchan777/tartine-scraper-bot.git`

1. ### ENV file setup
    - Place the token in your .env file with the format `bot_token = <bot token here>`
    - Sending a notification text requires a SMTP username, SMTP password, phone number of recipient, and recipient's cell phone carrier.
        - Place the SMTP username in your .env file with the format `email = <SMTP username here>`
        - Place the SMTP password in your .env file with the format `password = <SMTP password here>`
        - Place the notification receiver's information in your .env file with the format `receiver_email = <phone number>@<SMS gateway domain>`
            - Example: `receiver_email = <1234567890@tmomail.net>` for T-Mobile phone numbers

1. `pip3 install -r requirements.txt`

1. `python3 app.py`

## Commands
| Command 	| Description 	|
|-	|-	|
| `$country_v2` | Begins scraping. Scrapes for availability indefinitely every 60 seconds and displays information in the channel the command was called in.|

## Requirements
* Selenium
* Chrome Webdriver