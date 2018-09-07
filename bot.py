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
import re, pyrebase

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

config = {
  "apiKey": "AIzaSyDNsScR8JpErWjVxU3oUr3Th0GRGSW5GXA",
  "authDomain": "chat-wars-bots.firebaseapp.com",
  "databaseURL": "https://chat-wars-bots.firebaseio.com",
  "storageBucket": "chat-wars-bots.appspot.com",
  "serviceAccount": "serviceToken.json"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
items = db.child("items").get()

itemCodes = {}

for item in items.each():
   itemCodes[item.key()] = item.val()["id"]

print("Ready for processing")

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
            if f.__name__ == "error":
                return f(bot, update, context)
            else:
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
def refresh(bot, update):
    global itemCodes
    for item in db.child("items").get().each():
        itemCodes[item.key()] = item.val()["id"]
    update.message.reply_text("Item List updated!")

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
    if ("📃" in textLines[0] or "(recipe)" in textLines[0]) and ":" in textLines[0]:
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
updater = Updater(token, request_kwargs={'read_timeout': 10})
jobQ = updater.job_queue

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler("reset", reset))
dp.add_handler(CommandHandler("refresh", refresh))

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
