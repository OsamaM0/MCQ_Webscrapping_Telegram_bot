from modules import *
import logging
import logging.config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    PollHandler,
)
import telegram
from dotenv import load_dotenv, find_dotenv
import os
import time

##################################### USER & CHAT INFO #####################################
def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id


def get_user(update):
    user: User = None

    _from = None

    if update.message is not None:
        _from = update.message.from_user
    elif update.callback_query is not None:
        _from = update.callback_query.from_user

    if _from is not None:
        user = User()
        user.id = _from.id
        user.first_name = _from.first_name if _from.first_name is not None else ""
        user.last_name = _from.last_name if _from.last_name is not None else ""
        user.lang = _from.language_code if _from.language_code is not None else "n/a"

    logging.info(f"from {user}")

    return user
    

def new_member(update, context):
    logging.info(f"new_member : {update}")
    add_typing(update, context)
    add_text_message(update, context, f"New user")
    print("new User")



##################################### Telegram Send & Get Messages #######################################

def add_typing(update, context):
    context.bot.send_chat_action(
        chat_id=get_chat_id(update, context),
        action=telegram.ChatAction.TYPING,
        timeout=1,
    )
    time.sleep(1)

# Send Message
def add_text_message(update, context, message):
    context.bot.send_message(chat_id=get_chat_id(update, context), text=message)
# Receive Message
def get_text_from_message(update):
    return update.message.text

# Send Inline Keyboard Buttons
def add_suggested_actions(update, context, response):
    options = []

    for item in response:
        options.append(InlineKeyboardButton(item, callback_data=item))

    reply_markup = InlineKeyboardMarkup([options])

    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text="Choose Your Preferred Mode !" ,
        reply_markup=reply_markup,
    )
def get_text_from_callback(update):
    try:
        chosen =  update['callback_query']['data']
    except:
      chosen = None
    return chosen


# Send Quizz Message
def add_quiz_question(update, context, quiz_question,explanation, peroid=None):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.QUIZ,
        correct_option_id=quiz_question.correct_answer_position,
        open_period=peroid,
        is_anonymous=True,
        explanation=explanation,
        explanation_parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )



    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    context.bot_data.update({message.poll.id: message.chat.id})

# Send Poll Message
def add_poll_question(update, context, quiz_question):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.REGULAR,
        allows_multiple_answers=True,
        is_anonymous=False,
    )

def get_answer(update):
    answers = update.poll.options

    ret = ""

    for answer in answers:
        if answer.voter_count == 1:
            ret = answer.text

    return ret


# determine if user answer is correct
def is_answer_correct(update):
    answers = update.poll.options

    ret = False
    counter = 0

    for answer in answers:
        if answer.voter_count == 1 and update.poll.correct_option_id == counter:
            ret = True
            break
        counter = counter + 1

    return ret



def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" ', update)
    logging.exception(context.error)

def poll_handler(update, context):
    logging.info(f"question : {update.poll.question}")
    # logging.info(f"correct option : {update.poll.correct_option_id}")
    # logging.info(f"option #1 : {update.poll.options[0]}")
    # logging.info(f"option #2 : {update.poll.options[1]}")
    # logging.info(f"option #3 : {update.poll.options[2]}")
    # logging.info(f"option #4 : {update.poll.options[3]}")
    logging.info(f"correct option {is_answer_correct(update)}")
    print(update.poll)

