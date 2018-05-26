# DEV : Remnants, no need to modify
# -*- coding: utf-8 -*-
# If you use redis, install this add-on https://elements.heroku.com/addons/heroku-redis
#r = redis.from_url(os.environ.get("REDIS_URL"))

# DEV : Comment Syntax
# 		DEV - meant for Development-specific options or comments
#		DEF - variable/handler/import definitions and declarations
#		FUN - explains what functions do. Max 2 sentences
#		VAR - explains use of variable. Include which module it belongs to
#		LOG - meant for Logging/Debug-specific functions or comments
# 		EFF - catalogue side-effects that change things outside of the function

# DEV : Python Note
# Multiline strings in IDE can be done by escaping newline /[ENTER]
# Python can accept function parameters out of order. Just specify parameter name as defined in function declaration
# Split long function calls into multiple lines, with each parameter in its own line and named correctly
# Be careful of whitespace. Python is whitespace sensititve

# DEF : Imports
import os, telegram, re, logging
from collections import namedtuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# DEV : Replace this with dev token if you are testing out code
token = '553336581:AAFLrI6QY6B2wpcO0XimLyG43FjbuZhZkGQ'

# LOG : Logger declaration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# FUN : Sends message
def sendMsg(bot, msg, text, reply = False, keyboard = False):
	reply_id = None
	reply_markup_flag = None
	if (reply is True): 
		reply_id = msg.message_id
	if (keyboard is True):
		reply_markup_flag = markup
	return bot.sendMessage(
		chat_id = msg.chat_id,
		reply_to_message_id = reply_id,
		text = text,
		parse_mode = telegram.ParseMode.MARKDOWN,
		reply_markup = reply_markup_flag
	)

# FUN : Sends a reply message to msg
def replyMsg(bot, msg, text):
	sendMsg(bot, msg, text, reply = True)


# FUN : Returns true if in a group chat	
def inGroup(msg):
	return msg.chat.get_members_count() > 2

# FUN : Returns an identifiable name for chats
#       Groups use title as name
#       Private chats use their name	
def getChatName(msg):
	if inGroup(msg):
		return msg.chat.title
	else:
		return msg.chat.username

# LOG : Logs error
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

# DEF : Handlers

# HND : Handles /start. Required for API compliance
# FUN : Sends arbitrary startup message
# EFF : Registers private chats into local storage
def start(bot, update):
	sendMsg(bot, update.message, 'Hello World!')

# HND : Handles /hello. Required for API compliance
# FUN : Sends arbitrary greeting message
def hello(bot, update):
	replyMsg(bot, update.message, 'Hello {}'.format(update.message.from_user.first_name))
	
# HND : Handles /test.
# FUN : Sends arbitrary ping message
def test(bot, update):
	logger.info('{} from {} triggered {}'.format(update.message.from_user.first_name, getChatName(update.message), 'test'))
	replyMsg(bot, update.message, 'Test received {}'.format(update.message.from_user.first_name))

# HND : Handles /f.
# FUN : Sends Pay Respects meme
# EFF : Deletes trigger message
def payRespects(bot, update):
	logger.info('{} from {} triggered {}'.format(update.message.from_user.first_name, getChatName(update.message), 'respect'))
	sendMsg(bot, update.message, '{} has paid respects'.format(update.message.from_user.first_name))

# HND : Handles /shrug
# FUN : Sends ASCII shrug emoticon
# EFF : Deletes trigger message
def shrug(bot, update):
	sendMsg(bot, update.message, '{}: ¯\\\_(ツ)\_/¯'.format(update.message.from_user.first_name))


	
# HND : Registers handlers and updaters
updater = Updater(token)

dp = updater.dispatcher

# HND : Command Handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('hello', hello))
dp.add_handler(CommandHandler('test', test))

# HND : Error Handlers
dp.add_error_handler(error)

updater.start_polling()
updater.idle()