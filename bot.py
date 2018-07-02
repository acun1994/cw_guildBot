# DEF : Imports
import os, logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

# DEV : Replace this if using heroku
#token = os.environ["TELEGRAM_TOKEN"]
f = open("token", "r")
if f.mode == "r":
    token = f.read()

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
    "Bauxite"           : "11",
    #NYI                : "12",
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
    "Astrulic"          : "65",
    "Flammia Nut"       : "66",
    "Plexisop"          : "67",
    "Mammoth Dill"      : "68",
    "Silver dust"       : "69",
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
    "Vial of Mana"      : "p13",
    "Potion of Mana"    : "p14",
    "Bottle of Mana"    : "p15",
    "Vial of Twilight"  : "p16",
    "Potion of Twilight": "p17",
    "Bottle of Twilight": "p18",
    "Vial of Morph"     : "p19",
    "Potion of Morph"   : "p20",
    "Bottle of Morph"   : "p21",
    "Vial of Oblivion"  : "pl1",
    "Bottle of Oblivion": "pl3",
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
    "Rapier"            : "w07",
    "Halberd"           : "w12",
    "Mithril Dagger"    : "w17",
    "Forest Bow"        : "w22",
    "Mithril Axe"       : "w27",
    "Champion Sword"    : "w28",
    "Trident"           : "w29",
    "Hunter Bow"        : "w30",
    "War Hammer"        : "w31",
    "Hunter Dagger"     : "w32",
    "Mithril Armor"     : "a05",
    "Mithril Helmet"    : "a10",
    "Mithril Boots"     : "a15",
    "Mithril Gauntlets" : "a20",
    "Mithril Shield"    : "a25",
    "Order Armor"       : "a27",
    "Order Helmet"      : "a28",
    "Order Boots"       : "a29",
    "Order Gauntlets"   : "a30",
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
    "Champion blade"            : "k01",
    "Trident blade"             : "k02",
    "Hunter Shaft"              : "k03",
    "War Hammer head"           : "k04",
    "Hunter blade"              : "k05",
    "Order Armor piece"         : "k06",
    "Order Helmet fragment"     : "k07",
    "Order Boots part"          : "k08",
    "Order Gauntlets part"      : "k09",
    "Order Shield part"         : "k10",
    "Hunter Armor part"         : "k11",
    "Hunter Helmet fragment"    : "k12",
    "Hunter Boots part"         : "k13",
    "Hunter Gloves part"        : "k14",
    "Clarity Robe piece"        : "k15",
    "Clarity Circlet fragment"  : "k16",
    "Clarity Shoes part"        : "k17",
    "Clarity Bracers part"      : "k18",
    #
    # == Recipes ==
    #   
    "Champion Sword recipe"     : "r01",
    "Trident recipe"            : "r02",
    "Hunter Bow recipe"         : "r03",
    "War Hammer recipe"         : "r04",
    "Hunter Dagger recipe"      : "r05",
    "Order Armor recipe"        : "r06",
    "Order Helmet recipe"       : "r07",
    "Order Boots recipe"        : "r08",
    "Order Gauntlets recipe"    : "r09",
    "Order Shield recipe"       : "r10",
    "Hunter Armor recipe"       : "r11",
    "Hunter Helmet recipe"      : "r12",
    "Hunter Boots recipe"       : "r13",
    "Hunter Gloves recipe"      : "r14",
    "Clarity Robe recipe"       : "r15",
    "Clarity Circlet recipe"    : "r16",
    "Clarity Shoes recipe"      : "r17",
    "Clarity Bracers recipe"    : "r18"

    #
    # == King Parts ==
    #   

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
    update.message.reply_text('INLINE Bot usage: \n@cw_guildBot {itemName} {quantity}. \n\nItem Name does not have to be full, 3 characters is enough')
    update.message.reply_text('STANDARD Bot usage: \nForward a list of items e.g. /stock, Alchemy, Brewery Table')


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    actionText = "/g_deposit"

    results = []

    if query == '' or len(query) < 3:
        update.inline_query.answer(results)
        return

    queryString = query.split()

    if queryString[-1].upper() == "W":
        queryString = queryString[:-1]
        actionText = "/g_withdraw"

    if len(queryString) == 1:
        quantity = 1
    else:
        if not queryString[-1].isdigit():
            quantity = 1
        else:
            quantity = queryString[-1]
            queryString = queryString[:-1]

    listValidFinal = [key for key, value in itemCodes.items() if queryString[0] in key.lower()]
    
    if len(queryString) > 1:
        for ele in queryString[1:]:
            listValidFinal = list(set(listValidFinal).intersection([key for key, value in itemCodes.items() if ele in key.lower()]))   

    if len(listValidFinal) == 0:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title = "Not Found",
                input_message_content = InputTextMessageContent(
                    '{} not found'.format(" ".join(queryString))
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
                        "{} {} {}".format(actionText, itemCodes[key], quantity)
                    )
                )
            )

    update.inline_query.answer(results)

def process(bot, update):
    #https://t.me/share/url?url=/brew_60%20120 link format for auto forward
    """Process given /stock"""
    boolValid = False
    textLines = update.message.text.splitlines()
    if "📦" in textLines[0]:
        textLines = textLines[1:]
    
    if "/aa" in textLines[0]:
        textLines = [lines[7:] for lines in textLines]

    if ")" in textLines[0]:
        textLines = [lines[:-1] for lines in textLines]

    if "(" in textLines[0]:
        textLines = [a.split(" (") for a in textLines]
        boolValid = True
    elif " x " in textLines[0]:
        textLines  = [a.split(" x ") for a in textLines]
        boolValid = True

    if boolValid:
        replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_deposit%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0]], a[1],a[0], a[1]) for a in textLines])

        update.message.reply_text("DEPOSIT INTO GUILD \n{}".format(replyText), parse_mode="HTML")
    else:
        update.message.reply_text("Sorry, I don't understand your request. Please use /help for more information")
        bot.sendMessage(chat_id='-1001213337130',\
            text = 'CW - Unknown text received.\
                  \n Sender : \
                  \n  {} ({})\
                  \n Text:\
                  \n  {}'.format(update.message.from_user.first_name, update.message.from_user.username , update.message.text))

def error(bot, update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context)
    bot.sendMessage(chat_id='-1001213337130', text = ('CW - Error\n Update "%s" caused error "%s"', update, context))


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
dp.add_handler(MessageHandler(Filters.text, process))

# on Inline query
dp.add_handler(InlineQueryHandler(inlinequery))

# log all errors
dp.add_error_handler(error)

# Start the Bot
updater.start_polling()

# Block until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()