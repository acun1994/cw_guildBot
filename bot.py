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
token = os.environ['TELEGRAM_TOKEN']

# DEF : Class definitions
PersonChat = namedtuple('PersonChat', 'user chat_id chat_name')
Event = namedtuple('Event', 'username date name')
Pinned = namedtuple('Pinned', 'chat_id message_id')

# LOG : Logger declaration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# DEF : Global vars
# VAR : Tracking vars for event module
private_chats = []
events= []
lastEventCaller = ''

# VAR : Tracking var for pinned messages
pinnedMessages = []

# DEF : custom switch to receive query_data and currentName from button()
def textContentDict(arg, currentName):
	textContent = {
		'1': 'Hello {}'.format(currentName),
		'2': 'Test received {}'.format(currentName),
		'3': '{} has paid respects to art thou'.format(currentName),
		'4': '¯\\\_(ツ)\_/¯'
	}
	return textContent.get(arg, 'wtf u clicking m8')

# DEF : Regex for date pattern matching
#       Returns true for all valid dates between 010100 to 311299
#       Does not handle leap days
datePattern = re.compile("(0[1-9]|[1-2][0-9]|31(?!(?:0[2469]|11))|30(?!02))(0[1-9]|1[0-2])(\d{2})")

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

# FUN : Sends a prepared message according to custom keyboard
def keyboardMsg(bot, msg, text):
	sendMsg(bot, msg, text, keyboard = True)
	

# FUN : Pins a message
def pinMsg(bot, msg):
	bot.pinChatMessage(
		chat_id = msg.chat_id,
		message_id = msg.message_id,
		disable_notification = True
	)

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

# FUN : Deletes message specified as msg		
def delete(bot, msg):
	if inGroup(msg):
		logger.info('{} from {} triggered {}'.format(msg.from_user.first_name, getChatName(msg), 'delete'))
		del_msg_id = msg.message_id
		del_chat_id = msg.chat_id
		bot.deleteMessage(
			chat_id = del_chat_id, 
			message_id = del_msg_id
		)
	else:
		logger.info('Could not {} in private chat {}'.format('delete', getChatName(msg)))
	
# LOG : Logs error
def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

# DEF : Handlers

# HND : Handles /start. Required for API compliance
# FUN : Sends arbitrary startup message
# EFF : Registers private chats into local storage
def start(bot, update):
	sendMsg(bot, update.message, 'Hello World!')
	privateChatTuple = PersonChat(update.message.from_user, update.message.chat_id)
	if (privateChatTuple not in private_chats):
		private_chats.append(privateChatTuple)
		print (private_chats)

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
	delete(bot, update.message)

# HND : Handles /shrug
# FUN : Sends ASCII shrug emoticon
# EFF : Deletes trigger message
def shrug(bot, update):
	sendMsg(bot, update.message, '{}: ¯\\\_(ツ)\_/¯'.format(update.message.from_user.first_name))
	delete(bot, update.message)

# HND : Handles /pin
# FUN : Pins a bot-written message to the chat
# EFF : Chat has new pinned message
def pin(bot, update, args):
	if (len(args) == 0):
		replyMsg(bot, update.message, "Please specify what to pin")
		return

	text =' '.join(args)
	curPinnedMessage = bot.get_chat(update.message.chat_id).pinned_message

	if (curPinnedMessage is not None):
		pinnedMessageTuple = Pinned(update.message.chat_id, curPinnedMessage.message_id)

		if (update.message.chat_id in [x[0] for x in pinnedMessages]):
			pinnedMessages[:] = [pinnedMessageTuple if ele[0] == update.message.chat_id else ele for ele in pinnedMessages]
		else:
			pinnedMessages.append(pinnedMessageTuple)

	msg_id = sendMsg(bot, update.message, text)

	pinMsg(bot, msg_id)


# HND : Handles /unpin
# FUN : Replaces current pinned message with previous if available
def unpin(bot, update):
	curPinnedMessage = bot.get_chat(update.message.chat_id).pinned_message

	if (curPinnedMessage is not None):
		if (update.message.chat_id in [x[0] for x in pinnedMessages]):
			idx = [x[0] for x in pinnedMessages].index(update.message.chat_id)
			logger.info(pinnedMessages[idx])
			bot.pinChatMessage(
				chat_id = update.message.chat_id,
				message_id = pinnedMessages[idx][1],
				disable_notification = True	)
		else:
			bot.unpinChatMessage(update.message.chat_id)

# HND : Handles /event
# FUN : Module for event registering and recording. TODO : Split into multiple subfunctions for clarity
# EFF : Modifies local storage for events
def event(bot, update, args):
	if (len(args) == 0):
		replyMsg(bot, update.message, 
			"\n\
			To create an event, use the following command \n\
			`/event add [DDMMYY] [event name]` \nFor multi-word names, just type as usual \n\
			\nTo view events , use the command \n\
			`/event list`")
	
	elif (args[0] == 'list'):
		if (len(events) == 0):
			text = 'No events currently'
		else:
			text = '';
			for event in events:
				text = text + event.date + ' : ' + event.name + '\n'
				
		replyMsg(bot, update.message, text)
			
	elif (args[0] == 'add'):
		if (len(args) < 3):
			replyMsg(bot, update.message, 
				"\n\
				To create an event, use the following command \n\
				`/event add [DDMMYY] [event name]` \nFor multi-word names, just type as usual")
		elif (bool(datePattern.match(args[1])) == False):
			replyMsg(bot, update.message, "Please use `DDMMYY` format for date")
		
		else:
			addedEvent = Event(update.message.from_user.username, args[1], ' '.join(args[2:]))
			events.append(addedEvent)
			replyMsg(bot, update.message, "Event added")
			
	
	else:
		replyMsg(bot, update.message, 
			"\n\
			To create an event, use the following command \n\
			`/event add [DDMMYY] [event name]` \nFor multi-word names, just type as usual \n\
			\nTo view events , use the command \n\
			`/event list`")

# HND : Handles /command
# FUN : Creates custom inline keyboard layout with 4 functions preset
# EFF : pass callback_data to button() and delete /command
def command(bot, update):
	logger.info('{} from {} triggered {}'.format(update.message.from_user.first_name, getChatName(update.message), 'inlineLOL'))
	keyboard = [[InlineKeyboardButton("Hello", callback_data='1'), InlineKeyboardButton("Ping Me!", callback_data='2')],

                [InlineKeyboardButton("Pay Respect", callback_data='3'), InlineKeyboardButton("Shrug like AI Chan", callback_data='4')]]

	reply_markup = InlineKeyboardMarkup(keyboard)
	bot.sendMessage(update.message.chat_id, 'Hi! My name is AI, but you can call me AI chan. Anything that I can help you, {}?'.format(update.message.from_user.first_name), reply_markup=reply_markup)
	currentName = update.message.from_user.first_name
	logger.info('{}'.format(currentName))
	delete(bot, update.message)

# HND : Handles /command callback_data
# FUN : edit text depends on callback_data
# EFF : inline keyboard will be edited to textContent, depending on callback_data
def button(bot, update):
	query = update.callback_query

	bot.edit_message_text(text = textContentDict(query.data, update.callback_query.from_user.first_name),
                          chat_id = query.message.chat_id,
                          message_id = query.message.message_id,
						  parse_mode = telegram.ParseMode.MARKDOWN)
	
# HND : Registers handlers and updaters
updater = Updater(token)

dp = updater.dispatcher

# HND : Command Handlers
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('event', event, pass_args = True))
dp.add_handler(CommandHandler('pin', pin, pass_args = True))
dp.add_handler(CommandHandler('unpin', unpin))
dp.add_handler(CommandHandler('command', command))
dp.add_handler(CallbackQueryHandler(button))

# HND : Error Handlers
dp.add_error_handler(error)

updater.start_polling()
updater.idle()