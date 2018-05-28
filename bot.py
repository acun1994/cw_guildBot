# DEF : Imports
import os, logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

# DEV : Replace this with dev token if you are testing out code
token = os.environ["TELEGRAM_TOKEN"]

itemCodes = {
    #  
    # == Crafting Ingredients ==
    #
    "Thread"            : "01",
    "Stick"             : "02",
    "Pelt"              : "03",
    "Bone"              : "04",
    "Coal"              : "05",
    "Charcoal"          : "06",
    "Powder"            : "07",
    "Iron ore"          : "08",
    "Cloth"             : "09",
    "Silver ore"        : "10",
    "Magic stone"       : "13",
    "Wooden shaft"      : "14",
    "Sapphire"          : "15",
    "Solvent"           : "16",
    "Ruby"              : "17",
    "Hardener"          : "18",
    "Steel"             : "19",
    "Leather"           : "20",
    "Bone powder"       : "21",
    "String"            : "22",
    "Coke"              : "23",
    "Purified powder"   : "24",
    "Silver alloy"      : "25",
    #NYI                : "26",
    "Steel mold"        : "27",
    "Silver mold"       : "28",
    #NYI                : "29",
    #NYI                : "30", 
    "Rope"              : "31",
    #NYI                : "32", 
    "Metal plate"       : "33",
    "Metallic Fiber"    : "34",
    "Crafted Leather"   : "35",
    #NYI                : "36", 
    #NYI                : "37", 
    #NYI                : "38",
    #  
    # == Potion Ingredients ==
    #
    "Stinky Sumac"      : "39",
    "Mercy Sassafras"   : "40",
    "Cliff Rue"         : "41",
    "Love Creeper"      : "42",
    "Wolf Root"         : "43",
    "Swamp Lavender"    : "44",
    "White Blossom"     : "45",
    "Ilaves"            : "46",
    "Ephijora"          : "47",
    "Storm Hyssop"      : "48",
    "Cave Garlic"       : "49",
    "Yellow Seed"       : "50",
    "Tecceagrass"       : "51",
    "Spring Bay Leaf"   : "52",
    "Ash Rosemary"      : "53",
    "Sanguine Parsley"  : "54",
    "Sun Tarragon"      : "55",
    "Maccunut"          : "56",
    "Dragon Seed"       : "57",
    "Queen's Pepper"    : "58",
    "Plasma of abyss"   : "59",
    "Ultramarine dust"  : "60",
    "Ethereal bone"     : "61",
    "Itacory"           : "62",
    "Assassin Vine"     : "63",
    "Kloliarway"        : "64",
    #
    # == Potions ==
    #
    "Vial of Rage"      : "p01",
    "Potion of Rage"    : "p02",
    "Bottle of Rage"    : "p03",
    "Vial of Peace"     : "p04",
    "Potion of Peace"   : "p05",
    "Bottle of Peace"   : "p06",
    "Vial of Greed"     : "p07",
    "Potion of Greed"   : "p08",
    "Bottle of Greed"   : "p09",
    "Vial of Nature"    : "p10",
    "Potion of Nature"  : "p11",
    "Bottle of Nature"  : "p12",
    #
    # == Miscellaneous ==
    #
    "Pouch of Gold"     : "100",
    "Wrapping"          : "501",
    "Wooden arrows pack": "505",
    "Steel arrows pack" : "511",
    #
    # == Equippables ==
    #
    "Torch"             : "tch",
    "Champion Sword"    : "w28",
    "Trident"           : "w29",
    "Hunter Bow"        : "w30",
    "War Hammer"        : "w31",
    "Hunter Dagger"     : "w32",
    "Order Armor"       : "a27",
    "Order Helmet"      : "a28",
    "Order Boots"       : "a29",
    "Order Gauntlet"    : "a30",
    "Order Shield"      : "a31",
    "Hunter Armor"      : "a32",
    "Hunter Helmet"     : "a33",
    "Hunter Boots"      : "a34",
    "Hunter Gloves"     : "a35",
    "Clarity Robe"      : "a36",
    "Clarity Circlet"   : "a37",
    "Clarity Shoes"     : "a38",
    "Clarity Bracers"   : "a39",
    #
    # == Parts ==
    #
    "Champion Blade"            : "k01",
    "Trident Blade"             : "k02",
    "Hunter Shaft"              : "k03",
    "War Hammer Head"           : "k04",
    "Hunter Blade"              : "k05",
    "Order Armor Piece"         : "k06",
    "Order Helmet Fragment"     : "k07",
    "Order Boots Part"          : "k08",
    "Order Gauntlet Part"       : "k09",
    "Order Shield Part"         : "k10",
    "Hunter Armor Part"         : "k11",
    "Hunter Helmet Fragment"    : "k12",
    "Hunter Boots Part"         : "k13",
    "Hunter Gloves Part"        : "k14",
    "Clarity Robe Piece"        : "k15",
    "Clarity Circlet Fragment"  : "k16",
    "Clarity Shoes Part"        : "k17",
    "Clarity Bracers Part"      : "k18",
    #
    # == Recipes ==
    #   
    "Champion Sword Recipe"     : "r01",
    "Trident Recipe"            : "r02",
    "Hunter Bow Recipe"         : "r03",
    "War Hammer Recipe"         : "r04",
    "Hunter Dagger Recipe"      : "r05",
    "Order Armor Recipe"        : "r06",
    "Order Helmet Recipe"       : "r07",
    "Order Boots Recipe"        : "r08",
    "Order Gauntlet Recipe"     : "r09",
    "Order Shield Recipe"       : "r10",
    "Hunter Armor Recipe"       : "r11",
    "Hunter Helmet Recipe"      : "r12",
    "Hunter Boots Recipe"       : "r13",
    "Hunter Gloves Recipe"      : "r14",
    "Clarity Robe Recipe"       : "r15",
    "Clarity Circlet Recipe"    : "r16",
    "Clarity Shoes Recipe"      : "r17",
    "Clarity Bracers Recipe"    : "r18"
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
    update.message.reply_text('Bot usage: @cw_guildBot {itemName} {quantity}. \n\nItem Name does not have to be full, 3 characters is enough')


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query

    results = []

    if query == '' or len(query) < 3:
        update.inline_query.answer(results)
        return

    splitquery = query.split()
    
    if len(splitquery) == 1:
        queryString = splitquery
        quantity = 1
    else:
        if not splitquery[-1].isdigit():
            quantity = 1
        else:
            quantity = splitquery[-1]
            queryString = splitquery[:-1]
    
    listValidFinal = [key for key, value in itemCodes.items() if queryString[0] in key.lower()]
    if len(splitquery) > 1:
        listValid2 = [key for key, value in itemCodes.items() if queryString[1] in key.lower()]
        listValidFinal = list(set(listValidFinal).intersection(listValid2))
        if len(splitquery) > 2:
            listValid3 = [key for key, value in itemCodes.items() if queryString[2] in key.lower()]
            listValidFinal = list(set(listValidFinal).intersection(listValid3))
    

    if len(listValidFinal) == 0:
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
        for key in listValidFinal:  
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