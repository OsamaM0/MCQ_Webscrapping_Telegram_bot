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
from ._model import *
from telegram_used_fun import *

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
          os.remove(file_path)
    except:
          pass
    ######################### Listing For User Messages  #########################
    try: 
        if (update.message is not None):
            # QUIZ MODE SELECTION UPDATE PERIOD
            if (users_preference[user_id]["quiz_mode"]["mode"] == "quiz") and (users_preference[user_id]["quiz_mode"]["period"] == None):
                    period = get_text_from_message(update)
                    if period.isdigit():
                          users_preference[user_id]["quiz_mode"]["period"] = period
                          add_text_message(update, context, "What is the number of questions do you want for your Quiz ? ")
                    else:
                          add_text_message(update, context, f"Please Enter the period as number ") 
            # QUIZ MODE SELECTION UPDATE NUMBER      
            elif(users_preference[user_id]["quiz_mode"]["mode"] == "quiz") and  (users_preference[user_id]["quiz_mode"]["number"] == None):
                    number = get_text_from_message(update)
                    if number.isdigit():
                          users_preference[user_id]["quiz_mode"]["number"] = number
                          add_text_message(update, context, "Please Send Link/pdf You Want to Scrape")  
                    else:
                          add_text_message(update, context, f"Please Enter the number of questions as number ") 

            elif users_preference[user_id]["quiz_mode"]["mode"] == "":
                    print("link is send")
                    link = get_text_from_message(update)
                    if validat_link (update, context,link):
                        msq = Sanfoundry.scrape_questions(link)
                        quize_mode(update, context,number,period,msq)
                      
            # USER MSQs FILE/Link     
            elif get_text_from_message(update) not in ["/start", "/help","/mode"]:
                    # First check if user select any mode
                    if users_preference[user_id]["quiz_mode"]["mode"] == None:
                              add_text_message(update, context, f"Please Select Your Mode")
                              add_suggested_actions(update,context,["help","quiz","normal"])
                    # if user check any mode now scraping the file/link
                    else :
                          mode, period, number, degree = users_preference[user_id]["quiz_mode"].values()
                          # Scrape file
                          if (pdf_msq != None):
                                print("PDF is send")
                                quize_mode(update, context,number,period,pdf_msq)
                          # Scrape link
                          else:
                              print("link is send")
                              link = get_text_from_message(update)
                              if validat_link (update, context,link):
                                  msq = Sanfoundry.scrape_questions(link)
                                  quize_mode(update, context,number,period,msq)
    except Exception  as e:
      print(e)
                        
    # except Exception as e:
    #     print("Sending to quiz mode error: ",e)

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

############################### Commands Handler ####################################
def start_command_handler(update, context):
    """Send a message when the command /start is issued."""
    #Reset All Attributes 
    global users_preference
    user_id = update["_effective_user"]["id"]
    users_preference[user_id] = {"quiz_mode":{"mode":None,"period":None,"number":None,"degree":0}
                           ,"file_pref":{"question":"","options":"","answer":""}}
    add_text_message(update, context, f'Welcome : {update["_effective_user"]["first_name"]}  {update["_effective_user"]["last_name"]} at Q4K Quizzes Bot 😊 ')
    mode_command_handler(update, context)

  
    url = update.message.text
    # keyboard = [['Button 1', 'Button 2'], ['Button 3', 'Button 4']]
    # reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    # update.message.reply_text('Please select a button:', reply_markup=reply_markup)
   
def mode_command_handler(update, context):
    """ Select Preferred Mode when the command /mode is issued."""
    add_suggested_actions(update,context,["quiz","normal"])
    main_handler(update, context) 

def btn_link_command_handler(update, context):
    add_text_message(update, context, f'Enter Main Links That Have Sub Links For MSQs  ')

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
to choose your preferred mode please enter /mode
For Quiz   Mode Press ->  quiz
For Normal Mode Press ->  normal  

Developers Telegram Account: @Osama_Mo7

    '''

    update.message.reply_text(help_message)
  
###############################  Action Butoon Handlers ####################################
def action_button_handler(update, context):
          mode = get_text_from_callback(update)
          user_id = update["_effective_user"]["id"]
          global users_preference
          if mode == "quiz":
              add_text_message(update, context, " **You Choose Quiz Mode**")
              add_text_message(update, context, "What is the period do you want for your Quiz in minutes ? ")
              users_preference[user_id]["quiz_mode"]["mode"] = mode
            
          elif mode == "normal":
              add_text_message(update, context, " **You Choose Normal Mode** ")
              values = [mode, None, None, 0] 
              variable_names = ["mode", "period", "number", "degree"]
              users_preference[user_id]["quiz_mode"] = dict(zip(variable_names, values))
              add_text_message(update, context, "Please Send Link/pdf You Want to Scrape")
          elif mode == "help":
            help_command_handler(update, context)
  

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




#Keyboards links
def keyboard_links():
  links = 0
##################################### MAIN FUNCTION ########################################
def main():
    updater = Updater(os.environ.get("TELEGRAM_TOKEN", ""), use_context=True)

    dp = updater.dispatcher

    # command handlers
    dp.add_handler(CommandHandler("help", help_command_handler))
    dp.add_handler(CommandHandler("start", start_command_handler))
    dp.add_handler(CommandHandler("mode", mode_command_handler))


    # message handler
    dp.add_handler(MessageHandler(Filters.text, main_handler))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    # file andler
    dp.add_handler(MessageHandler(Filters.document, main_handler))

    # suggested_actions_handler
    dp.add_handler(
        CallbackQueryHandler(action_button_handler, pass_chat_data=True, pass_user_data=True)
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

