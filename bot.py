# DEF : Imports
import os, logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import escape_markdown
from telegram.error import (TelegramError, Unauthorized, BadRequest, 
                            TimedOut, ChatMigrated, NetworkError)

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
    # == crafting ingredients ==
    #
    "thread" : "01",
    "stick" : "02",
    "pelt" : "03",
    "bone" : "04",
    "coal" : "05",
    "charcoal" : "06",
    "powder" : "07",
    "iron ore" : "08",
    "cloth" : "09",
    "silver ore" : "10",
    "bauxite" : "11",
    "cord" : "12",
    "magic stone" : "13",
    "wooden shaft" : "14",
    "sapphire" : "15",
    "solvent" : "16",
    "ruby" : "17",
    "hardener" : "18",
    "steel" : "19",
    "leather" : "20",
    "bone powder" : "21",
    "string" : "22",
    "coke" : "23",
    "purified powder" : "24",
    "silver alloy" : "25",
    #"mithril alloy" : "26",
    "steel mold" : "27",
    "silver mold" : "28",
    "blacksmith frame" : "29",
    "artisan frame" : "30", 
    "rope" : "31",
    "silver frame" : "32", 
    "metal plate" : "33",
    "metallic fiber" : "34",
    "crafted leather" : "35",
    #nyi : "36", 
    #nyi : "37", 
    #nyi : "38",
    # 
    # == potion ingredients ==
    #
    "stinky sumac" : "39",
    "mercy sassafras" : "40",
    "cliff rue" : "41",
    "love creeper" : "42",
    "wolf root" : "43",
    "swamp lavender" : "44",
    "white blossom" : "45",
    "ilaves" : "46",
    "ephijora" : "47",
    "storm hyssop" : "48",
    "cave garlic" : "49",
    "yellow seed" : "50",
    "tecceagrass" : "51",
    "spring bay leaf" : "52",
    "ash rosemary" : "53",
    "sanguine parsley" : "54",
    "sun tarragon" : "55",
    "maccunut" : "56",
    "dragon seed" : "57",
    "queen's pepper" : "58",
    "plasma of abyss" : "59",
    "ultramarine dust" : "60",
    "ethereal bone" : "61",
    "itacory" : "62",
    "assassin vine" : "63",
    "kloliarway" : "64",
    "astrulic" : "65",
    "flammia nut" : "66",
    "plexisop" : "67",
    "mammoth dill" : "68",
    "silver dust" : "69",
    #
    # == potions ==
    #
    "vial of rage" : "p01",
    "potion of rage" : "p02",
    "bottle of rage" : "p03",
    "vial of peace" : "p04",
    "potion of peace" : "p05",
    "bottle of peace" : "p06",
    "vial of greed" : "p07",
    "potion of greed" : "p08",
    "bottle of greed" : "p09",
    "vial of nature" : "p10",
    "potion of nature" : "p11",
    "bottle of nature" : "p12",
    "vial of mana" : "p13",
    "potion of mana" : "p14",
    "bottle of mana" : "p15",
    "vial of twilight" : "p16",
    "potion of twilight": "p17",
    "bottle of twilight": "p18",
    "vial of morph" : "p19",
    "potion of morph" : "p20",
    "bottle of morph" : "p21",
    "vial of оblivion" : "pl1",
    "bottle of oblivion": "pl3",
    #
    # == miscellaneous ==
    #
    "pouch of gold" : "100",
    "wrapping" : "501",
    "wooden arrow" : "504",
    "wooden arrows pack": "505",
    "bottle of remedy" : "506",
    "remedy pack" : "507",
    "bottle of poison" : "508",
    "poison pack" : "509",
    "steel arrow" : "510",
    "steel arrows pack" : "511",
    "silver arrow" : "512",
    "silver arrows pack": "513",
    "🎟gift coupon 'pig'": "514",
    "🎟gift coupon 'horse'": "515",
    "🎟gift coupon 'owl'": "516",
    "🎟gift coupon 'mouse'": "517",
    "🎟gift coupon 'gopher'": "522",
    "hay": "518",
    "corn": "519",
    "hamsters": "520",
    "cheese": "521",
    #
    # == equippables ==
    #
    "torch" : "tch",
    "cloth jacket":"a01",
    "leather shirt":"a02",
    "chain mail":"a03",
    "silver cuirass":"a04",
    "mithril armor":"a05",
    "hat":"a06",
    "leather hood":"a07",
    "steel helmet":"a08",
    "silver helmet":"a09",
    "mithril helmet":"a10",
    "sandals":"a11",
    "leather shoes":"a12",
    "steel boots":"a13",
    "silver boots":"a14",
    "mithril boots":"a15",
    "gloves":"a16",
    "leather gloves":"a17",
    "steel gauntlets":"a18",
    "silver gauntlets":"a19",
    "mithril gauntlets":"a20",
    "wooden shield":"a21",
    "skeleton buckler":"a22",
    "bronze shield":"a23",
    "silver shield":"a24",
    "mithril shield":"a25",
    "royal guard cape":"a26",
    "order armor":"a27",
    "order helmet":"a28",
    "order boots":"a29",
    "order gauntlets":"a30",
    "order shield":"a31",
    "hunter armor":"a32",
    "hunter helmet":"a33",
    "hunter boots":"a34",
    "hunter gloves":"a35",
    "clarity robe":"a36",
    "clarity circlet":"a37",
    "clarity shoes":"a38",
    "clarity bracers":"a39",
    "✏️pencil of truth":"a40",
    "bard's cape":"a41",
    "crusader armor":"a45",
    "crusader helmet":"a46",
    "crusader boots":"a47",
    "crusader gauntlets":"a48",
    "crusader shield":"a49",
    "royal armor":"a50",
    "royal helmet":"a51",
    "royal boots":"a52",
    "royal gauntlets":"a53",
    "royal shield":"a54",
    "ghost armor":"a55",
    "ghost helmet":"a56",
    "ghost boots":"a57",
    "ghost gloves":"a58",
    "lion armor":"a59",
    "lion helmet":"a60",
    "lion boots":"a61",
    "lion gloves":"a62",
    "demon robe":"a63",
    "demon circlet":"a64",
    "demon shoes":"a65",
    "demon bracers":"a66",
    "divine robe":"a67",
    "divine circlet":"a68",
    "divine shoes":"a69",
    "divine bracers":"a70",
    "storm cloak":"a71",
    "durable cloak":"a72",
    "blessed cloak":"a73",
    "hiking jar":"a74",
    "hiking bag":"a75",
    "champion blade":"k01",
    "trident blade":"k02",
    "hunter shaft":"k03",
    "war hammer head":"k04",
    "hunter blade":"k05",
    "order armor piece":"k06",
    "order helmet fragment":"k07",
    "order boots part":"k08",
    "order gauntlets part":"k09",
    "order shield part":"k10",
    "hunter armor part":"k11",
    "hunter helmet fragment":"k12",
    "hunter boots part":"k13",
    "hunter gloves part":"k14",
    "clarity robe piece":"k15",
    "clarity circlet fragment":"k16",
    "clarity shoes part":"k17",
    "clarity bracers part":"k18",
    "thundersoul blade":"k19",
    "doomblade blade":"k20",
    "eclipse blade":"k21",
    "guard's blade":"k22",
    "king's defender blade":"k23",
    "raging lance blade":"k24",
    "composite bow shaft":"k25",
    "lightning bow shaft":"k26",
    "hailstorm bow shaft":"k27",
    "imperial axe head":"k28",
    "skull crusher head":"k29",
    "dragon mace head":"k30",
    "ghost blade":"k31",
    "lion blade":"k32",
    "crusader armor piece":"k33",
    "crusader helmet fragment":"k34",
    "crusader boots part":"k35",
    "crusader gauntlets part":"k36",
    "crusader shield part":"k37",
    "royal armor piece":"k38",
    "royal helmet fragment":"k39",
    "royal boots part":"k40",
    "royal gauntlets part":"k41",
    "royal shield part":"k42",
    "ghost armor part":"k43",
    "ghost helmet fragment":"k44",
    "ghost boots part":"k45",
    "ghost gloves part":"k46",
    "lion armor part":"k47",
    "lion helmet fragment":"k48",
    "lion boots part":"k49",
    "lion gloves part":"k50",
    "demon robe piece":"k51",
    "demon circlet fragment":"k52",
    "demon shoes part":"k53",
    "demon bracers part":"k54",
    "divine robe piece":"k55",
    "divine circlet fragment":"k56",
    "divine shoes part":"k57",
    "divine bracers part":"k58",
    "storm cloak part" : "k59",
    "durable cloak part":"k60",
    "blessed cloak part":"k61",
    "champion sword recipe":"r01",
    "trident recipe":"r02",
    "hunter bow recipe":"r03",
    "war hammer recipe":"r04",
    "hunter dagger recipe":"r05",
    "order armor recipe":"r06",
    "order helmet recipe":"r07",
    "order boots recipe":"r08",
    "order gauntlets recipe":"r09",
    "order shield recipe":"r10",
    "hunter armor recipe":"r11",
    "hunter helmet recipe":"r12",
    "hunter boots recipe":"r13",
    "hunter gloves recipe":"r14",
    "clarity robe recipe":"r15",
    "clarity circlet recipe":"r16",
    "clarity shoes recipe":"r17",
    "clarity bracers recipe":"r18",
    "thundersoul sword recipe":"r19",
    "doomblade sword recipe":"r20",
    "eclipse recipe":"r21",
    "guard's spear recipe":"r22",
    "king's defender recipe":"r23",
    "raging lance recipe":"r24",
    "composite bow recipe":"r25",
    "lightning bow recipe":"r26",
    "hailstorm bow recipe":"r27",
    "imperial axe recipe":"r28",
    "skull crusher recipe":"r29",
    "dragon mace recipe":"r30",
    "ghost dagger recipe":"r31",
    "lion knife recipe":"r32",
    "crusader armor recipe":"r33",
    "crusader helmet recipe":"r34",
    "crusader boots recipe":"r35",
    "crusader gauntlets recipe":"r36",
    "crusader shield recipe":"r37",
    "royal armor recipe":"r38",
    "royal helmet recipe":"r39",
    "royal boots recipe":"r40",
    "royal gauntlets recipe":"r41",
    "royal shield recipe":"r42",
    "ghost armor recipe":"r43",
    "ghost helmet recipe":"r44",
    "ghost boots recipe":"r45",
    "ghost gloves recipe":"r46",
    "lion armor recipe":"r47",
    "lion helmet recipe":"r48",
    "lion boots recipe":"r49",
    "lion gloves recipe":"r50",
    "demon robe recipe":"r51",
    "demon circlet recipe":"r52",
    "demon shoes recipe":"r53",
    "demon bracers recipe":"r54",
    "divine robe recipe":"r55",
    "divine circlet recipe":"r56",
    "divine shoes recipe":"r57",
    "divine bracers recipe":"r58",
    "storm cloak recipe":"r59",
    "durable cloak recipe":"r60",
    "blessed cloak recipe":"r61",
    "📕scroll of rage":"s01",
    "📕scroll of peace":"s02",
    "📗scroll of rage":"s03",
    "📗scroll of peace":"s04",
    "📘scroll of rage":"s05",
    "📘scroll of peace":"s06",
    "📕rare scroll of rage":"s11",
    "📕rare scroll of peace":"s12",
    "📗rare scroll of rage":"s13",
    "📗rare scroll of peace":"s14",
    "📘rare scroll of rage":"s15",
    "📘rare scroll of peace":"s16",
    "wooden sword":"w01",
    "short sword":"w02",
    "long sword":"w03",
    "widow sword":"w04",
    "knight's sword":"w05",
    "elven sword":"w06",
    "rapier":"w07",
    "short spear":"w08",
    "long spear":"w09",
    "lance":"w10",
    "elven spear":"w11",
    "halberd":"w12",
    "kitchen knife":"w13",
    "battle knife":"w14",
    "steel dagger":"w15",
    "silver dagger":"w16",
    "mithril dagger":"w17",
    "short bow":"w18",
    "wooden bow":"w19",
    "long bow":"w20",
    "elven bow":"w21",
    "forest bow":"w22",
    "club":"w23",
    "bone club":"w24",
    "heavy club":"w25",
    "steel axe":"w26",
    "mithril axe":"w27",
    "champion sword":"w28",
    "trident":"w29",
    "hunter bow":"w30",
    "war hammer":"w31",
    "hunter dagger":"w32",
    "thundersoul sword":"w33",
    "doomblade sword":"w34",
    "eclipse":"w35",
    "guard's spear":"w36",
    "king's defender":"w37",
    "raging lance":"w38",
    "composite bow":"w39",
    "lightning bow":"w40",
    "hailstorm bow":"w41",
    "imperial axe":"w42",
    "skull crusher":"w43",
    "dragon mace":"w44",
    "ghost dagger":"w45",
    "lion knife":"w46",
    "loyalty trophy":"tlt",
    "🎂cake":"e6",
    "🎂special cake":"e7",
    "🎂rare cake":"e8",
    "🍫chocolate":"e9",
    "💝valentine's card":"vc",
    "🎁assistant's box":"bx1",
    "zombie box":"bx3",
    "zombie chest":"ch1",
    "hunter kit":"hk",
    #Cant be transferred, but keeping just in case
    # "ichor":"ich",
    # "key":"key",
    "accuracy pill":"pap",
    "garlic stew":"pgs",
    "holy water":"phw",
    "monster pheromones":"pmp",
    "silver blood":"psb",
    "vial of defiance":"pvd",
    "elder's recommendation":"er",
    "🦌deerhorn earloom":"tde",
    "🐉dragonscale earloom":"tdr",
    "🐺wolfpack earloom":"two",
    "🥔potato earloom":"tpo",
    "🦈sharkteeth earloom":"tsh",
    "🦅highnest earloom":"thi"
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
        except IndexError as e:
            if update and update.message  :
                update.message.reply_text("No transferrable items found")
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

            template = "CW Guild - ERROR \nUser: {2} ({3})\nAn exception of type {0} occurred\nArguments:\n{1!r}\nText :\n{4}"
            message = template.format(type(e).__name__, e.args, firstname, username, text)
            bot.send_message(chat_id='-1001213337130',
                             text=message, parse_mode = ParseMode.HTML)
    return wrap

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
@catch_error
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Bot Name : `CW (EU) Guild Inventory Helper`\n\
Developer : @acun1994\n\
Special Thanks: @wolvix and @Knightniwrem for breaking the bot\n\
Description : \n\
Bot that assists in guild inventory management (Deposit, Withdraw)\n\
Use /help for more info', parse_mode=ParseMode.MARKDOWN)

@catch_error
def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('INLINE Bot usage: \n@cw_guildBot {itemName} {quantity} {"w" (optional, to withdraw)}. \n\nItem Name does not have to be full, 3 characters is enough.\n\
STANDARD Bot usage: \nForward a list of items. Should support all inventories.\n\n\
RECIPE Bot usage: \nForward the recipe text as received from CW.\n\n\
WARNING: Enchanted and unique items will NOT be processed\n\n\
Poke @acun1994 if you find something that isn\'t handled yet')

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

    update.inline_query.answer(results, cache_time = None, is_personal = True)

@catch_error
def process(bot, update):
    #https://t.me/share/url?url=/brew_60%20120 link format for auto forward
    """Process given /stock"""
    if not update.message:
        return
    boolValid = False
    boolRecipe = False
    boolGuild = False
    boolMissing = False
    textLines = update.message.text.splitlines()

    #Filter out blacklist
    textLines = [line for line in textLines if "Ichor" not in line and "Key" not in line]
    
    #Individual recipe. Waiting for action
    if "📃" in textLines[0] or "(recipe)" in textLines[0]:
        update.message.reply_text("Please reply to the recipe text with [d]eposit or [w]ithdraw ")
        return

    #Storage
    if "📦" in textLines[0]:
        textLines = textLines[1:]

    #Guild Warehouse
    if "Guild" in textLines[0]:
        boolGuild = True
        textLines = [line.split(" ",1)[1] for line in textLines[1:]]

    #Missing ingredients
    elif "Not" in textLines[0]:
        textLines = textLines[2:]
        boolMissing = True
    
    #Brewery
    elif "/aa" in textLines[0]:
        textLines = [line[7:] for line in textLines]

    #Workbench
    elif "/a_" in textLines[0]:
        textLines = [line[7:] if line[6] == ' ' else line[6:] for line in textLines]

    #Misc
    elif "/use" in textLines[0]:
        textLines = [line[:-10] if line[:-1] == ' ' else line if "Wrap" in line or "Card" in line or "Coupon" in line else line[:-9] for line in textLines]
    
    #Auction
    elif len(textLines) > 1 and "/lot" in textLines[1]:
        textLines = [line[9:] for line in textLines[1:-5]]

    #Crafting
    textLines = [remove_emoji(line)[:-10] if "view" in line else line for line in textLines]

    #Equipment
    textLines = [remove_emoji(line)[:-10] if "bind" in line else line for line in textLines]

    #Individual recipe
    if update.message.reply_to_message:
        recipeAction = None
        
        if "w" in textLines[0].lower():
            recipeAction = "Withdraw"
        elif "d" in textLines[0].lower():
            recipeAction = "Deposit"
        
        if recipeAction:
            recipeText = update.message.reply_to_message.text.splitlines()
            if "(recipe)" in recipeText[0]:
                boolRecipe = True
                recipeTitle = "Ingredient List for \n<b>{}</b>".format(remove_emoji(recipeText[0])[:-10])
                if "Type" in recipeText[1]:
                    recipeText = recipeText[3:]
                else:
                    recipeText = recipeText[2:]

                textLines = recipeText

    #Remove trailing whitespace for Misc
    textLines = [line[:-1] if line[:-1] == ' ' else line for line in textLines]

    #Filter out uniques
    textLines = [line for line in textLines if "+" not in line and "Sign" not in line]

    if "(" in textLines[0]:
        textLines = [line.split(")")[0] for line in textLines]
        textLines = [line.split(" (") for line in textLines]
        boolValid = True
    elif " x " in textLines[0]:
        textLines  = [line.split(" x ") for line in textLines]
        boolValid = True
        if boolMissing:
            textLines = [[line[1], line[0]] for line in textLines]

    global proccessCount
    if boolRecipe:
        proccessCount = proccessCount+1

        if recipeAction == "Deposit":
            replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_deposit%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0].lower()], a[1],a[0], a[1]) for a in textLines])
        elif recipeAction == "Withdraw":
            replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_withdraw%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0].lower()], a[1],a[0], a[1]) for a in textLines])

        update.message.reply_text("{} {}\n{}".format(recipeAction, recipeTitle, replyText), parse_mode="HTML")
        return
    elif boolGuild or boolMissing:
        proccessCount = proccessCount+1

        replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_withdraw%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0].lower()], a[1],a[0], a[1]) for a in textLines])

        update.message.reply_text("WITHDRAW FROM GUILD\n{}".format(replyText), parse_mode="HTML")
        return
    elif boolValid:
        proccessCount = proccessCount+1

        replyText = "\n".join(["<a href='https://t.me/share/url?url=/g_deposit%20{}%20{}'>{}</a> x {}".format(itemCodes[a[0].lower()], a[1],a[0], a[1]) for a in textLines])

        update.message.reply_text("DEPOSIT INTO GUILD\n{}".format(replyText), parse_mode="HTML")
        return
    else:
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
    
    try:
        raise context
    except BadRequest:
        return
    except TimedOut:
        return
    except TelegramError:
        logger.warning('Update "%s" caused error "%s"', update, context)
        bot.sendMessage(chat_id='-1001213337130', text = 'CW - <b>Telegram Error</b>\n Update "{}" caused error "{}"'.format(update, context), parse_mode = "HTML")
        return
    except Exception:
        logger.warning('Update "%s" caused error "%s"', update, context)
        bot.sendMessage(chat_id='-1001213337130', text = 'CW - <b>Error</b>\n Update "{}" caused error "{}"'.format(update, context), parse_mode = "HTML")

def status(bot, job):
    messID = 287 #276 for dev, #287 for live
    bot.edit_message_text(  chat_id = '-1001213337130',
                            message_id = messID, 
                            text = "CW STATUS - `OK` : `{}`\nERRORS : **{}**\nPROCESSED : **{}**".format(
                                datetime.now().time().strftime('%H:%M'), 
                                errorCount,
                                proccessCount),
                            parse_mode = ParseMode.MARKDOWN)


def reset(bot, update):
    global proccessCount, errorCount
    lastID = bot.sendMessage(chat_id='-1001213337130', text = 'CW - Trackers reset').message_id

    for messID in range(287+1, lastID):#276 for dev, #287 for live
        try:
            bot.deleteMessage(chat_id='-1001213337130', message_id = messID)
        except TelegramError:
            continue

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
dp.add_handler(CommandHandler("reset", reset))

# Schedule
jobQ.run_repeating(status, interval=60, first = 0)

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, process))

# on Inline query
dp.add_handler(InlineQueryHandler(inlinequery))

# log all errors
dp.add_error_handler(error)

# Start the Bot
updater.start_polling(clean = True)

# Block until the user presses Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
