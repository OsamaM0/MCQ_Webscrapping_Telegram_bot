import time
import pyfiglet
import logging
import logging.config
import os
import validators
import random
from dotenv import load_dotenv, find_dotenv
from Scrapper import Sanfoundry , pdf
from server import server
from _model import *

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

################################### Attribute ###################################
global btn_pressed, period, number
btn_pressed = None
period = 's'
number = 's'

global users_preference
users_preference = {}

# Main Function To Handel all messages, /start command 
def main_handler(update, context):
    global users_preference
    user_id = update["_effective_user"]["id"]
    
    try:
          logging.info(f'update : {update["_effective_user"]["first_name"]}  {update["_effective_user"]["last_name"]} ')
    except:
          pass
      
    ################################## Listing For User Send File  ##################################
    pdf_msq = None
    try:
          file_path = context.bot.get_file(update.message.document).download()
          pdf_msq = pdf.get_msq_from_text(file_path)

    except:
          pass

    ######################### Listing For User Action Button Pressed  #########################
    if get_text_from_callback(update) is not None:
          mode = get_text_from_callback(update)
          if mode == "quiz":
              add_text_message(update, context, " **You Choose Quiz Mode** \n------------------\nSend each value in one line \n\nperiod of Quiz in minutes \nNumber of Questions")
              users_preference[user_id]["quiz_mode"]["mode"] = mode


          elif mode == "normal":
              values = [mode, None, None, 0] 
              variable_names = ["mode", "period", "number", "degree"]
              users_preference[user_id]["quiz_mode"] = dict(zip(variable_names, values))
              add_text_message(update, context, "Please Send Link/pdf You Want to Scrappe")

          elif mode == "help":
            mode == "help"
            help_command_handler(update, context)

    ######################### Listing For User Messages  #########################
    try:
      if (update.message is not None):
          # MODE SELECTION 
          if (users_preference[user_id]["quiz_mode"]["mode"] == "quiz") and (users_preference[user_id]["quiz_mode"]["period"] == None):

                  user_input = get_text_from_message(update)
                  try:
                    
                    p, n = user_input.split('\n')
                    logging.info(f"user_input : {user_input}")
                    if p.isdigit() and  n.isdigit():
                      # Update User  quiz_mode Data
                      period, number = p, n 
                      values = ["quiz", period, number, 0] 
                      variable_names = [" mode", "period", "number", "degree"]
                      users_preference[user_id]["quiz_mode"] = dict(zip(variable_names, values))
                      add_text_message(update, context, "Please Send Link/pdf You Want to Scrappe")  
                    else:
                      add_text_message(update, context, f"Please Enter\nperiod as number \nnumber of questions as number") 
                  except Exception  as e :
                    add_text_message(update, context, f"Please Enter\nperiod\nnumber of questions")
                    print(e)
          elif get_text_from_message(update) not in ["/start", "/help"]:
              if users_preference[user_id]["quiz_mode"]["mode"] == None:
                        add_text_message(update, context, f"Please Select Your Mode")
                        add_suggested_actions(update,context,["help","quiz","normal"])

              else :
                    mode, period, number, degree = users_preference[user_id]["quiz_mode"].values()
                    if (pdf_msq != None):
                          add_text_message(update, context, "**NOTE**\n to get all quizzes correctly the pdf must contain\n*number before question head\n*Character [A-D] before each option \n*Word Answer before correct answer charcter")
                          quize_mode(update, context,number,period,pdf_msq)
                          os.remove(file_path)
                    else:
                        link = get_text_from_message(update)
                        if validat_link (update, context,link):
                            msq = Sanfoundry.scrape_questions(link)
                            quize_mode(update, context,number,period,msq)
                        
    except Exception as e:
        print("Sending to quiz mode error: ",e)

        # ban member
        # m = context.bot.kick_chat_member(
        #     chat_id="-1001572091573", #get_chat_id(update, context),
        #     user_id='1041389347',
        #     timeout=int(time.time() + 86400))
        #
        # logging.info(f"kick_chat_member : {m}")

# Function Cheack Link
def validat_link (update, context,link):
      validation = validators.url(link)
      if validation  :
        # reply
        add_typing(update, context)
        add_text_message(update, context, f"You type: {link}")
        if "www.sanfoundry.com" in link:
            return True
        else:
          add_text_message(update, context, f"Please Enter Only Sanfoundry Link or pdf")   
          return False
      else:
          add_text_message(update, context, f"Please Enter Valid Link For Sanfoundry Page You Want or pdf") 
          return Falase

############################### Functions That Handel Commands ####################################
def start_command_handler(update, context):
    """Send a message when the command /start is issued."""
    #Reset All Attributes 
    global users_preference
    user_id = update["_effective_user"]["id"]
    users_preference[user_id] = {"quiz_mode":{"mode":None,"period":None,"number":None,"degree":0}
                           ,"file_pref":{"question":"","options":"","answer":""}}
    add_text_message(update, context, f'Welcome : {update["_effective_user"]["first_name"]}  {update["_effective_user"]["last_name"]} at Q4K Quizzes Bot 😊 ')
    add_suggested_actions(update,context,["help","quiz","normal"])
    main_handler(update, context)
  
    url = update.message.text


def help_command_handler(update, context):
    """Send a message when the command /help is issued."""
    help_message = r'''**This is Q4K Quiz Bot**
    -----------------------------------
    
Just Give the bot link or pdf file and it will send Questions From them as Telegram Quiz
    
You Can Web Scraping Web Page Like
    - Sanfoundry Websites 

Or You Can Give the bot pdf file

There are 2 Mode 
    1- Quiz Mode -> Make Quiz For you With
        . particular Time
        . particular Number Of Questions that you want 
    2- Normal Mode -> Just Get All Question without any time 
    
For Quiz   Mode Press ->  \quiz
For Normal Mode Press ->  \normal  

Developers Telegram Account: @Osama_Mo7

    '''

    update.message.reply_text(help_message)


############################ Important Functions ##############################################

# Take Question Dect & Send The Quizzes 
def quize_mode(update, context,number,peroid,msq):
    """Send a message when the command /quiz is issued."""
    questions = msq
    print(questions)
    if number is not None:
      number = int(number)
      peroid = int(peroid) * 60
      if len(questions) < number:
          add_text_message(update, context,"The Number You Entered Bigger Than number of questions from link you provided") 
      else:
          # Shuffle The Dict To Make Quiz
          random.shuffle(questions)
          questions = questions[:number]
        
    for question in questions:
        try:
            quiz_question = QuizQuestion()
            quiz_question.question = question["question"]
            quiz_question.answers = question["options"]
            quiz_question.correct_answer_position = question["answer"]
            add_quiz_question(update, context, quiz_question,f'{question["explanation"]}', peroid)
        
            for l_que in question["long_question"]:
              try:
                add_text_message(update, context,l_que)
              except:
                pass
            

            for img_link in question["images"]:
              try:
                  add_text_message(update, context,img_link)
              except:
                pass

  
        except Exception as e:
            print("error ",e)






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

    user_answer = get_answer(update)
    logging.info(f"correct option {is_answer_correct(update)}")



##################################### MAIN FUNCTION ########################################
def main():
    updater = Updater("6014793546:AAHmUrtaCVEIHWpU_xZYaFMYirJtu-fDbik", use_context=True)

    dp = updater.dispatcher

    # command handlers
    dp.add_handler(CommandHandler("help", help_command_handler))
    dp.add_handler(CommandHandler("start", start_command_handler))

    # message handler
    dp.add_handler(MessageHandler(Filters.text, main_handler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # file andler
    dp.add_handler(MessageHandler(Filters.document, main_handler))

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
    server()
    ascii_banner = pyfiglet.figlet_format("SampleTelegramQuiz")
    print(ascii_banner)

    # Enable logging
    DefaultConfig.init_logging()

    main()
