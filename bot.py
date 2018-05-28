# DEF : Imports
import os, logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

# DEV : Replace this with dev token if you are testing out code
#token = '553336581:AAFLrI6QY6B2wpcO0XimLyG43FjbuZhZkGQ'
token = os.environ["TELEGRAM_TOKEN"]

itemCodes = {
    "Spring Bay Leaf": "52",
    "Bottle of Peace": "p06",
    "Bottle of Greed": "p09",
    "Dragon Seed": "57",
    "Bottle of Nature": "p12",
    "Vial of Nature": "p10",
    "Potion of Nature": "p11",
    "Love Creeper": "42",
    "Wolf Root": "43",
    "Wooden arrows pack": "505",
    "Sapphire": "15",
    "Steel mold": "27",
    "Wooden shaft": "14",
    "Silver mold": "28",
    "Solvent": "16",
    "Rope": "31",
    "Silver alloy": "25",
    "Steel arrows pack": "511",
    "Purified powder": "24",
    "Hardener": "18",
    "Magic stone": "13",
    "Ruby": "17",
    "Metal plate": "33",
    "Silver ore": "10",
    "Kloliarway": "64",
    "Bottle of Rage": "p03",
    "Ilaves": "46",
    "Itacory": "62",
    "Yellow Seed": "50",
    "Assassin Vine": "63",
    "Potion of Rage": "p02",
    "Queen's Pepper": "58",
    "Swamp Lavender": "44",
    "Cave Garlic": "49",
    "Sanguine Parsley": "54",
    "White Blossom": "45",
    "Ash Rosemary": "53",
    "Mercy Sassafras": "40",
    "Ultramarine dust": "60",
    "Stinky Sumac": "39",
    "Plasma of abyss": "59",
    "Potion of Peace": "p05",
    "Potion of Greed": "p08",
    "Sun Tarragon": "55",
    "Vial of Greed": "p07",
    "Storm Hyssop": "48",
    "Cliff Rue": "41",
    "Bone": "04",
    "Powder": "07",
    "Coke": "23",
    "String": "22",
    "Charcoal": "06",
    "Ephijora": "47",
    "Leather": "20",
    "Coal": "05",
    "Tecceagrass": "51",
    "Stick": "02",
    "Thread": "01",
    "Steel": "19",
    "Bone powder": "21",
    "Cloth": "09",
    "Pelt": "03",
    "Wrapping": "501",
    "Torch": "tch",
    "Vial of Peace": "p04",
    "Vial of Rage": "p01",
    "Ethereal bone": "61",
    "Iron ore": "08",
    "Maccunut": "56"
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query

    results = []

    if query == '' or len(query) < 3:
        update.inline_query.answer(results)
        return

    splitquery = query.split()
    
    if len(splitquery) == 1:
        queryString = query
    else:
        queryString = " ".join(splitquery[:-1])

    quantity = 1

    if not splitquery[-1].isdigit():
        quantity = 1
    else:
        quantity = splitquery[-1]
    
    listValid = [key for key, value in itemCodes.items() if queryString in key.lower()]

    if len(listValid) == 0:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title = "Not Found",
                input_message_content = InputTextMessageContent(
                    '{} not found'.format(queryString)
                )
            )
        ]

    else:
        for key in listValid:  
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title = "{} x{}".format(key, quantity),
                    input_message_content = InputTextMessageContent(
                        '/g_deposit {} {}'.format(itemCodes[key], quantity)
                    )
                )
            )

    update.inline_query.answer(results)


def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context)

# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(token)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(InlineQueryHandler(inlinequery))

# log all errors
dp.add_error_handler(error)

# Start the Bot
updater.start_polling()

# Block until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()