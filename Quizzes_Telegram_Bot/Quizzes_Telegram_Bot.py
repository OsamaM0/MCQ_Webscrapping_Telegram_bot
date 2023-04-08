import time
import datetime

import pyfiglet
import logging
import logging.config
import os
from bs4 import BeautifulSoup
import requests
import re
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

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

from _model import *


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

# Web scraping function to extract questions and answers
def scrape_questions(url):
    url = url
    soup = ""
    while True:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            break
        except:
            pass
    
    questions = []
    for questions_p in soup.find_all('div', {'class': 'entry-content'}):
        for question, ans in zip(questions_p.findAll("p")[1:-3],questions_p.find_all('div', {'class': 'collapseomatic_content'})) :
            try:
                q = {}
                ques = modifiStr(str(question)).split("<br/>")
                q['question'] = ques[0][3:]
                if (len(ques[1])<100) and (len(ques[2])<100 ) and (len(ques[3])<100) and (len(ques[4])<100 ) :
                    q['options'] = ques[1:5]
                else:
                    if (len(ques[1])<100) and (len(ques[2])<100 ):
                        q['options'] = [ques[1],ques[2],"c) None Of above","d) All of both answers"]
                    else:

                            s = q['question'].split("<br>")
                            q['question'] = s[0]
                            q['options'] = [s[1][:100],ques[1][:100],"c) None Of above","d) All of both answers"]

                    
                ans = modifiStr(str(ans)).split("<br/>")
                alpha = {"a":0,"b":1,"c":2,"d":3}
                q["answer"] = alpha[ ans[0].strip()[-1]]
                try:
                    q['explanation'] = ans[1][:-6]
                except: 
                        q['explanation']  = "No explanation"
                print(ans[1][:-6])
                questions.append(q)
            except Exception as e :
                print(e)
    return questions

def modifiStr (str):
    replace_chars = ['-', '(',')',"!","$","@","#","\\","|"]
    pattern = "[" + "".join(replace_chars) + "]"
    new_string = re.sub(pattern, ' ', str)
    return new_string
    


def start_command_handler(update, context):

    add_text_message(update, context,"Please Enter URL That You Want To Get Quizzes From")
    url = update.message.text



    
    
    

def quize_command_handler(update, context,url):
    """Send a message when the command /start is issued."""
    add_typing(update, context)

    for question in scrape_questions(url):
        try:
            quiz_question = QuizQuestion()
            quiz_question.question = question["question"]
            quiz_question.answers = question["options"]
            quiz_question.correct_answer_position = question["answer"]
            quiz_question.correct_answer = question["explanation"]
            add_quiz_question(update, context, quiz_question,f'{question["explanation"].replace("."," ")}')
        except Exception as e:
            print("error ",e)



def help_command_handler(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Type /start")


def new_member(update, context):
    logging.info(f"new_member : {update}")


    add_typing(update, context)
    add_text_message(update, context, f"New user")


def main_handler(update, context):
    logging.info(f"update : {update}")

    if update.message is not None:
        user_input = get_text_from_message(update)
        logging.info(f"user_input : {user_input}")

        # reply
        add_typing(update, context)
        add_text_message(update, context, f"You type: {user_input}")
        if len(user_input) > 10:
            quize_command_handler(update, context,user_input)

        # ban member
        # m = context.bot.kick_chat_member(
        #     chat_id="-1001572091573", #get_chat_id(update, context),
        #     user_id='1041389347',
        #     timeout=int(time.time() + 86400))
        #
        # logging.info(f"kick_chat_member : {m}")


def poll_handler(update, context):
    logging.info(f"question : {update.poll.question}")
    logging.info(f"correct option : {update.poll.correct_option_id}")
    logging.info(f"option #1 : {update.poll.options[0]}")
    logging.info(f"option #2 : {update.poll.options[1]}")
    logging.info(f"option #3 : {update.poll.options[2]}")
    logging.info(f"option #4 : {update.poll.options[3]}")

    user_answer = get_answer(update)
    logging.info(f"correct option {is_answer_correct(update)}")

    add_typing(update, context)
    #add_text_message(update, context, f"Correct answer is {user_answer}")


def add_typing(update, context):
    context.bot.send_chat_action(
        chat_id=get_chat_id(update, context),
        action=telegram.ChatAction.TYPING,
        timeout=1,
    )
    time.sleep(1)


def add_text_message(update, context, message):
    context.bot.send_message(chat_id=get_chat_id(update, context), text=message)


def add_suggested_actions(update, context, response):
    options = []

    for item in response.items:
        options.append(InlineKeyboardButton(item, callback_data=item))

    reply_markup = InlineKeyboardMarkup([options])

    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text=response.message,
        reply_markup=reply_markup,
    )


# def add_quiz_question(update, context, quiz_question):
#     message = context.bot.send_poll(
#         chat_id=get_chat_id(update, context),
#         question=quiz_question.question,
#         options=quiz_question.answers,
#         type=Poll.QUIZ,
#         correct_option_id=quiz_question.correct_answer_position,
#         open_period=5,
#         is_anonymous=True,
#         explanation="Well, honestly that depends on what you eat",
#         explanation_parse_mode=telegram.ParseMode.MARKDOWN_V2,
#     )
def add_quiz_question(update, context, quiz_question,explanation):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.QUIZ,
        correct_option_id=quiz_question.correct_answer_position,
        is_anonymous=True,
        explanation=explanation,
        explanation_parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )


    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    context.bot_data.update({message.poll.id: message.chat.id})


def add_poll_question(update, context, quiz_question):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.REGULAR,
        allows_multiple_answers=True,
        is_anonymous=False,
    )


def get_text_from_message(update):
    return update.message.text


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


def get_text_from_callback(update):
    return update.callback_query.data


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" ', update)
    logging.exception(context.error)


def main():
    updater = Updater("6014793546:AAHmUrtaCVEIHWpU_xZYaFMYirJtu-fDbik", use_context=True)

    dp = updater.dispatcher

    # command handlers
    dp.add_handler(CommandHandler("help", help_command_handler))
    dp.add_handler(CommandHandler("start", start_command_handler))

    # message handler
    dp.add_handler(MessageHandler(Filters.text, main_handler))

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # suggested_actions_handler
    dp.add_handler(
        CallbackQueryHandler(main_handler, pass_chat_data=True, pass_user_data=True)
    )

    # quiz answer handler
    dp.add_handler(PollHandler(poll_handler, pass_chat_data=True, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if DefaultConfig.MODE == "webhook":

        updater.start_webhook(
            listen="0.0.0.0",
            port=int(DefaultConfig.PORT),
            url_path=DefaultConfig.TELEGRAM_TOKEN,
        )
        updater.bot.setWebhook(DefaultConfig.WEBHOOK_URL + DefaultConfig.TELEGRAM_TOKEN)

        logging.info(f"Start webhook mode on port {DefaultConfig.PORT}")
    else:
        updater.start_polling()
        logging.info(f"Start polling mode")

    updater.idle()


class DefaultConfig:
    PORT = int(os.environ.get("PORT", 3978))
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    MODE = os.environ.get("MODE", "polling")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def init_logging():
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=DefaultConfig.LOG_LEVEL,
        )


if __name__ == "__main__":
    ascii_banner = pyfiglet.figlet_format("SampleTelegramQuiz")
    print(ascii_banner)

    # Enable logging
    DefaultConfig.init_logging()

    main()
