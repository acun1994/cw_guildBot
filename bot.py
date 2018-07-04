# DEF : Imports
import os, logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown

from functools import wraps
from datetime import datetime
import re

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

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
    "Cord"              : "12",
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
    "Mithril alloy"     : "26",
    "Steel mold"        : "27",
    "Silver mold"       : "28",
    "Blacksmith frame"  : "29",
    "Artisan frame"     : "30", 
    "Rope"              : "31",
    #NYI                : "32", 
    "Metal plate"       : "33",
    "Metallic fiber"    : "34",
    "Crafted leather"   : "35",
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
    "Pouch of gold"     : "100",
    "Wrapping"          : "501",
    "Wooden arrow"      : "504",
    "Wooden arrows pack": "505",
    "Bottle of Remedy"  : "506",
	"Remedy Pack"       : "507",
	"Bottle of Poison"  : "508",
	"Poison Pack"       : "509",
    "Steel arrow"       : "510",
    "Steel arrows pack" : "511",
    "Silver arrow"      : "512",
    "Silver arrows pack": "513",
    #
    # == Equippables ==
    #
    "Torch"             : "tch",
    "Cloth jacket":"a01",
    "Leather shirt":"a02",
    "Chain mail":"a03",
    "Silver cuirass":"a04",
    "Mithril armor":"a05",
    "Hat":"a06",
    "Leather hood":"a07",
    "Steel helmet":"a08",
    "Silver helmet":"a09",
    "Mithril helmet":"a10",
    "Sandals":"a11",
    "Leather shoes":"a12",
    "Steel boots":"a13",
    "Silver boots":"a14",
    "Mithril boots":"a15",
    "Gloves":"a16",
    "Leather gloves":"a17",
    "Steel gauntlets":"a18",
    "Silver gauntlets":"a19",
    "Mithril gauntlets":"a20",
    "Wooden shield":"a21",
    "Skeleton Buckler":"a22",
    "Bronze shield":"a23",
    "Silver shield":"a24",
    "Mithril shield":"a25",
    "Royal Guard Cape":"a26",
    "Order Armor":"a27",
    "Order Helmet":"a28",
    "Order Boots":"a29",
    "Order Gauntlets":"a30",
    "Order Shield":"a31",
    "Hunter Armor":"a32",
    "Hunter Helmet":"a33",
    "Hunter Boots":"a34",
    "Hunter Gloves":"a35",
    "Clarity Robe":"a36",
    "Clarity Circlet":"a37",
    "Clarity Shoes":"a38",
    "Clarity Bracers":"a39",
    "✏️Pencil of Truth":"a40",
    "Bard's Cape":"a41",
    "Crusader Armor":"a42",
    "Crusader Helmet":"a43",
    "Crusader Boots":"a44",
    "Crusader Gauntlets":"a45",
    "Crusader Shield":"a46",
    "Royal Armor":"a47",
    "Royal Helmet":"a48",
    "Royal Boots":"a49",
    "Royal Gauntlets":"a50",
    "Royal Shield":"a51",
    "Ghost Armor":"a52",
    "Ghost Helmet":"a53",
    "Ghost Boots":"a54",
    "Ghost Gloves":"a55",
    "Lion Armor":"a56",
    "Lion Helmet":"a57",
    "Lion Boots":"a58",
    "Lion Gloves":"a59",
    "Demon Robe":"a60",
    "Demon Circlet":"a61",
    "Demon Shoes":"a62",
    "Demon Bracers":"a63",
    "Divine Robe":"a64",
    "Divine Circlet":"a65",
    "Divine Shoes":"a66",
    "Divine Bracers":"a67",
    "Durable Cloak":"a69",
    "Blessed Cloak":"a70",
    "Champion blade":"k01",
    "Trident blade":"k02",
    "Hunter shaft":"k03",
    "War hammer head":"k04",
    "Hunter blade":"k05",
    "Order Armor piece":"k06",
    "Order Helmet fragment":"k07",
    "Order Boots part":"k08",
    "Order Gauntlets part":"k09",
    "Order shield part":"k10",
    "Hunter Armor part":"k11",
    "Hunter Helmet fragment":"k12",
    "Hunter Boots part":"k13",
    "Hunter Gloves part":"k14",
    "Clarity Robe piece":"k15",
    "Clarity Circlet fragment":"k16",
    "Clarity Shoes part":"k17",
    "Clarity Bracers part":"k18",
    "Thundersoul blade":"k19",
    "Doomblade blade":"k20",
    "Eclipse blade":"k21",
    "Guard's blade":"k22",
    "King's Defender blade":"k23",
    "Raging Lance blade":"k24",
    "Composite Bow shaft":"k25",
    "Lightning Bow shaft":"k26",
    "Hailstorm Bow shaft":"k27",
    "Imperial Axe head":"k28",
    "Skull Crusher head":"k29",
    "Dragon Mace head":"k30",
    "Ghost blade":"k31",
    "Lion blade":"k32",
    "Crusader Armor piece":"k33",
    "Crusader Helmet fragment":"k34",
    "Crusader Boots part":"k35",
    "Crusader Gauntlets part":"k36",
    "Crusader Shield part":"k37",
    "Royal Armor piece":"k38",
    "Royal Helmet fragment":"k39",
    "Royal Boots part":"k40",
    "Royal Gauntlets part":"k41",
    "Royal Shield part":"k42",
    "Ghost Armor part":"k43",
    "Ghost Helmet fragment":"k44",
    "Ghost Boots part":"k45",
    "Ghost Gloves part":"k46",
    "Lion Armor part":"k47",
    "Lion Helmet fragment":"k48",
    "Lion Boots part":"k49",
    "Lion Gloves part":"k50",
    "Demon Robe piece":"k51",
    "Demon Circlet fragment":"k52",
    "Demon Shoes part":"k53",
    "Demon Bracers part":"k54",
    "Divine Robe piece":"k55",
    "Divine Circlet fragment":"k56",
    "Divine Shoes part":"k57",
    "Divine Bracers part":"k58",
    "Durable Cloak part":"k60",
    "Blessed Cloak part":"k61",
    "Champion Sword recipe":"r01",
    "Trident recipe":"r02",
    "Hunter Bow recipe":"r03",
    "War hammer recipe":"r04",
    "Hunter Dagger recipe":"r05",
    "Order Armor recipe":"r06",
    "Order Helmet recipe":"r07",
    "Order Boots recipe":"r08",
    "Order Gauntlets recipe":"r09",
    "Order shield recipe":"r10",
    "Hunter Armor recipe":"r11",
    "Hunter Helmet recipe":"r12",
    "Hunter Boots recipe":"r13",
    "Hunter Gloves recipe":"r14",
    "Clarity Robe recipe":"r15",
    "Clarity Circlet recipe":"r16",
    "Clarity Shoes recipe":"r17",
    "Clarity Bracers recipe":"r18",
    "Thundersoul Sword recipe":"r19",
    "Doomblade Sword recipe":"r20",
    "Eclipse recipe":"r21",
    "Guard's Spear recipe":"r22",
    "King's Defender recipe":"r23",
    "Raging Lance recipe":"r24",
    "Composite Bow recipe":"r25",
    "Lightning Bow recipe":"r26",
    "Hailstorm Bow recipe":"r27",
    "Imperial Axe recipe":"r28",
    "Skull Crusher recipe":"r29",
    "Dragon Mace recipe":"r30",
    "Ghost Dagger recipe":"r31",
    "Lion Dagger recipe":"r32",
    "Crusader Armor recipe":"r33",
    "Crusader Helmet recipe":"r34",
    "Crusader Boots recipe":"r35",
    "Crusader Gauntlets recipe":"r36",
    "Crusader Shield recipe":"r37",
    "Royal Armor recipe":"r38",
    "Royal Helmet recipe":"r39",
    "Royal Boots recipe":"r40",
    "Royal Gauntlets recipe":"r41",
    "Royal Shield recipe":"r42",
    "Ghost Armor recipe":"r43",
    "Ghost Helmet recipe":"r44",
    "Ghost Boots recipe":"r45",
    "Ghost Gloves recipe":"r46",
    "Lion Armor recipe":"r47",
    "Lion Helmet recipe":"r48",
    "Lion Boots recipe":"r49",
    "Lion Gloves recipe":"r50",
    "Demon Robe recipe":"r51",
    "Demon Circlet recipe":"r52",
    "Demon Shoes recipe":"r53",
    "Demon Bracers recipe":"r54",
    "Divine Robe recipe":"r55",
    "Divine Circlet recipe":"r56",
    "Divine Shoes recipe":"r57",
    "Divine Bracers recipe":"r58",
    "Durable Cloak recipe":"r60",
    "Blessed Cloak recipe":"r61",
    "📕Scroll of Rage":"s01",
    "📕Scroll of Peace":"s02",
    "📗Scroll of Rage":"s03",
    "📗Scroll of Peace":"s04",
    "📕Rare Scroll of Rage":"s11",
    "📕Rare Scroll of Peace":"s12",
    "📗Rare Scroll of Rage":"s13",
    "📗Rare Scroll of Peace":"s14",
    "Wooden sword":"w01",
    "Short sword":"w02",
    "Long sword":"w03",
    "Widow sword":"w04",
    "Knight's sword":"w05",
    "Elven sword":"w06",
    "Rapier":"w07",
    "Short spear":"w08",
    "Long spear":"w09",
    "Lance":"w10",
    "Elven spear":"w11",
    "Halberd":"w12",
    "Kitchen knife":"w13",
    "Battle knife":"w14",
    "Steel dagger":"w15",
    "Silver dagger":"w16",
    "Mithril dagger":"w17",
    "Short Bow":"w18",
    "Wooden Bow":"w19",
    "Long Bow":"w20",
    "Elven Bow":"w21",
    "Forest Bow":"w22",
    "Club":"w23",
    "Bone club":"w24",
    "Heavy club":"w25",
    "Steel axe":"w26",
    "Mithril axe":"w27",
    "Champion Sword":"w28",
    "Trident":"w29",
    "Hunter Bow":"w30",
    "War hammer":"w31",
    "Hunter dagger":"w32",
    "Thundersoul Sword":"w33",
    "Doomblade Sword":"w34",
    "Eclipse":"w35",
    "Guard's Spear":"w36",
    "King's Defender":"w37",
    "Raging Lance":"w38",
    "Composite Bow":"w39",
    "Lightning Bow":"w40",
    "Hailstorm Bow":"w41",
    "Imperial Axe":"w42",
    "Skull Crusher":"w43",
    "Dragon Mace":"w44",
    "Ghost Dagger":"w45",
    "Lion Dagger":"w46"
}

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

errorCount = 0
proccessCount = 0

def catch_error(f):
    @wraps(f)
    def wrap(bot, update, context = ""):
        try:
            return f(bot, update)
        except Exception as e:
            logger.error(str(e))
            global errorCount 
            errorCount = errorCount + 1

            firstname = "Bot"   
            username = "-"
            text = "None"
            if update and update.message  :
                update.message.reply_text("Sorry, I have encountered an error. My master has been informed. Please use /help for more information")
                firstname = update.message.from_user.first_name
                text = update.message.text
                if update.message.from_user.username:
                    username = update.message.from_user.username

            template = "CW - ERROR \nUser: {2} ({3})\nAn exception of type {0} occurred.Arguments:\n{1!r}.Text :\n{4}"
            message = template.format(type(e).__name__, e.args, firstname, username, text)
            bot.send_message(chat_id='-1001213337130',
                             text=message)
    return wrap

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
@catch_error
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Bot Name : `CW (EU) Guild Assistant`\n\
Developer : @acun1994\n\
Description : \n\
Bot that assists in guild inventory management (Deposit, Withdraw)\n\
Use \help for more info', parse_mode=ParseMode.MARKDOWN)

@catch_error
def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('INLINE Bot usage: \n@cw_guildBot {itemName} {quantity} {"w" (optional, to withdraw)}. \n\nItem Name does not have to be full, 3 characters is enough')
    update.message.reply_text('STANDARD Bot usage: \nForward a list of items \nCurrently supports `/stock`, `Alchemy`, `/more`\nBeta support for `Equipment`, `Misc`', parse_mode=ParseMode.MARKDOWN)
    update.message.reply_text('Poke @acun1994 if you find something that isn\'t handled yet')

@catch_error
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

@catch_error
def process(bot, update):
    #https://t.me/share/url?url=/brew_60%20120 link format for auto forward
    """Process given /stock"""
    if not update.message:
        return
    boolValid = False
    textLines = update.message.text.splitlines()

    if len(textLines) > 1:
        if "📦" in textLines[0]:
            textLines = textLines[1:]
        
        if "/aa" in textLines[0]:
            textLines = [line[7:] for line in textLines]

        elif "/a_" in textLines[0]:
            textLines = [line[7:] if line[6] == ' ' else line[6:] for line in textLines]

        elif "/use" in textLines[0]:
            textLines = [line[:-10] if line[:-1] == ' ' or line[:-1] == ' ' else line[:-9] for line in textLines]
        
        elif "/lot" in textLines[1]:
            textLines = [line[9:] for line in textLines[1:-5]]

        textLines = [remove_emoji(line)[:-10] if "view" in line else line for line in textLines]
        textLines = [remove_emoji(line)[:-10] if "bind" in line else line for line in textLines]
        textLines = [line[:-1] if line[:-1] == ' ' else line for line in textLines]
        textLines = [line for line in textLines if "+" not in line]

        if ")" in textLines[0]:
            textLines = [line.split(")")[0] for line in textLines]

        if "(" in textLines[0]:
            textLines = [a.split(" (") for a in textLines]
            boolValid = True
        elif " x " in textLines[0]:
            textLines  = [a.split(" x ") for a in textLines]
            boolValid = True

        if boolValid:
            global proccessCount
            proccessCount = proccessCount+1
            replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_deposit%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0]], a[1],a[0], a[1]) for a in textLines])

            update.message.reply_text("DEPOSIT INTO GUILD \n{}".format(replyText), parse_mode="HTML")
            return
    
    global errorCount
    errorCount = errorCount+1
    update.message.reply_text("Sorry, I don't understand your request. Please use /help for more information")
    bot.sendMessage(chat_id='-1001213337130',\
        text = 'CW - Unknown text received.\
                \n<b>Sender</b> : \
                \n<pre>{} ({})</pre>\
                \n<b>Text</b>:\
                \n<pre>{}</pre>'.format(update.message.from_user.first_name, update.message.from_user.username , update.message.text),
                parse_mode = "HTML")

@catch_error
def error(bot, update, context = ""):
    """Log Errors caused by Updates."""
    if update is None: return
    logger.warning('Update "%s" caused error "%s"', update, context)
    bot.sendMessage(chat_id='-1001213337130', text = 'CW - <b>Error</b>\n Update "{}" caused error "{}"'.format(update, context), parse_mode = "HTML")

def status(bot, job):
    global proccessCount, errorCount
    bot.edit_message_text(  chat_id = '-1001213337130', 
                            message_id = 287, #276 for dev
                            text = "CW STATUS - `OK` : `{}`\nERRORS : **{}**\nPROCESSED : **{}**".format(
                                        datetime.now().time().strftime('%H:%M'), 
                                        errorCount,
                                        proccessCount),
                        parse_mode = ParseMode.MARKDOWN)

    errorCount = 0
    proccessCount = 0

# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context baspls ed callbacks
# Post version 12 this will no longer be necessary
updater = Updater(token)
jobQ = updater.job_queue

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))

# Schedule
jobQ.run_repeating(status, interval=900, first = 0)

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