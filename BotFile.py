import telebot
import os

import telebot.custom_filters
from Detector import DocScan
import requests
import cv2
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from modules.compressor import compress

state_storage = StateMemoryStorage()

token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token, state_storage=state_storage)

class MyStates(StatesGroup):
    got_image = State()
    got_size = State()
    got_res = State()


def docScanner(message):
    # print(file)
    with bot.retrieve_data(message.from_user.id,message.chat.id) as data:
        file =bot.get_file(data['file_id'])
    response= requests.get(f"https://api.telegram.org/file/bot{token}/{file.file_path}")
    with open("input/temp.jpg","wb") as f:
        f.write(response.content)
    
    image = cv2.imread("input/temp.jpg")
    scanner = DocScan(final_output=True)
    image, dest = scanner.scan(image)
    bot.send_photo(message.chat.id, open(dest,"rb"),reply_markup=ReplyKeyboardRemove())

    os.remove("input/temp.jpg")
    os.remove(dest)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state="*", commands=['cancel'])
def cancel_task(message):
    bot.send_message(message.chat.id, "Your task was cancelled")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.got_image)
def utility_selector(message):
    print(message.text)

    if message.text == "Scanner":
        docScanner(message)
    elif message.text == "Compressor":
        bot.send_message(message.chat.id,"Enter the target size in KB or 0 to skip",reply_markup=ReplyKeyboardRemove())
        bot.set_state(message.from_user.id, MyStates.got_size, message.chat.id)
    else:
        bot.send_message(message.chat.id,"Looks like you selected wrong option, Try Again",reply_markup=ReplyKeyboardRemove())


@bot.message_handler(state=MyStates.got_size, is_digit=True)
def got_size(message):
    with bot.retrieve_data(message.from_user.id,message.chat.id) as data:
        data['target_size'] = int(message.text)
    bot.set_state(message.from_user.id, MyStates.got_res, message.chat.id)
    bot.send_message(message.chat.id,"""
Enter the Target Resolution: Example 1280X720
Enter 1 to keep the same resolution
Enter 0 to auto-adjust the resolution
""")

@bot.message_handler(state=MyStates.got_size, is_digit=False)
def wrong_size(message):
    bot.send_message(message.chat.id, "It doesnot look like a number")




@bot.message_handler(state=MyStates.got_res)
def got_res(message):
    if message.text=='0':
        res=0
    elif message.text=='1':
        res=1
    else:
        try:
            res = tuple(map(int,message.text.split('X')))
        except:
            bot.send_message(message.chat.id,"Wrong Input, Please Try again...")
            return
        if len(res) != 2:
            bot.send_message(message.chat.id,"Resolution is wrong")
            return
        
    with bot.retrieve_data(message.from_user.id,message.chat.id) as data:
        file = bot.get_file(data['file_id'])
        response= requests.get(f"https://api.telegram.org/file/bot{token}/{file.file_path}")
        with open("input/temp.jpg","wb") as f:
            f.write(response.content)
        output_path,quality,final_res =compress("input/temp.jpg",data['target_size'],res)

    bot.send_message(message.chat.id,f"""
The file has been reduced to {int(os.path.getsize(output_path)/1024)}Kb
The resolution has been reduced to {final_res}
The quality is reduced to {quality}
    """)
    bot.send_document(message.chat.id,open(output_path,'rb'))
    os.remove("input/temp.jpg")
    os.remove(output_path)
    bot.delete_state(message.from_user.id, message.chat.id)




@bot.message_handler(content_types=['photo'])
def image_receiver(message):
    

    reply_markup= ReplyKeyboardMarkup()
    reply_markup.add("Scanner","Compressor", row_width=2)

    bot.send_message(message.chat.id, "Image recieved", reply_markup=reply_markup)
    bot.set_state(message.from_user.id, MyStates.got_image, message.chat.id)
    print("State Set")
    with bot.retrieve_data(message.from_user.id,message.chat.id) as data:
            data['file_id'] = message.photo[-1].file_id
    
bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.add_custom_filter(telebot.custom_filters.IsDigitFilter())

bot.infinity_polling()