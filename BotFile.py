import telebot
import os
from datetime import datetime
import time

import telebot.custom_filters
from Detector import DocScan
import requests
import cv2
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from modules.compressor import compress
from modules.PDF import generate_pdf, password_protect

state_storage = StateMemoryStorage()

token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token, state_storage=state_storage,threaded=False)
input_prefix = "input/"

class MyStates(StatesGroup):
    got_image = State()
    got_size = State()
    got_res = State()
    get_images = State()


def delete_data(path:str):
    try:
        for file in os.listdir(path):
            os.remove(path+file)
        os.rmdir(path)
    except Exception as e:
        print(e)


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
    path = input_prefix+str(message.from_user.id)+"/"
    delete_data(path)
    
    bot.send_message(message.chat.id, "Your task was cancelled")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.get_images,content_types="photo")
def recieve_images_for_pdf(message):
    image_path = input_prefix+str(message.from_user.id)+"/"+str(datetime.now()).replace(" ","_").replace(".","_").replace(":","_")+".jpg"
    try:
        open(image_path,"rb")
        time.sleep(1)
        image_path = input_prefix+str(message.from_user.id)+"/"+str(datetime.now()).replace(" ","_").replace(".","_").replace(":","_")+".jpg"
    except:
        pass
        
    # print(image_path)
    photo = message.photo[-1]
    file = bot.get_file(photo.file_id)
    content = bot.download_file(file.file_path)

    with open(image_path,"wb") as img:
        img.write(content)

@bot.message_handler(state=MyStates.get_images,commands=['create'])
def create_pdf(message):
    folder_path = input_prefix+str(message.from_user.id)+"/"
    wait_message = bot.send_message(message.chat.id,"Please Wait....")
    pdf_path = folder_path + str(datetime.now()).replace(" ","_").replace(".","_").replace(":","_")+".pdf"
    generate_pdf(folder_path,output=pdf_path,add_watermark=True,custom_watermark="Harkirat`s Image Utilities")

    try:
        with open(folder_path+"password.txt","r") as pwd_file:
            password = pwd_file.read()
            pdf_path = password_protect(folder_path,pdf_path.split("/")[-1],password)

    except:
        pass

    try:
        with open(folder_path+"name.txt","r") as name_file:
            new_name = folder_path + name_file.read() + ".pdf"
            os.rename(pdf_path,new_name)
            pdf_path = new_name

    except:
        pass

    bot.send_document(message.chat.id,open(pdf_path,"rb"))
    bot.delete_message(wait_message.chat.id, wait_message.message_id)
    print(message.from_user.first_name+" just made a PDF")
    path = input_prefix+str(message.from_user.id)+"/"
    delete_data(path)
    bot.delete_state(message.from_user.id,message.chat.id)
    


@bot.message_handler(state=MyStates.get_images)
def post_images(message):
    folder_path = input_prefix+str(message.from_user.id)+"/"
    try:
        command,value = message.text.split(":")
        if(command.lower()=="password"):
            with open(folder_path+"password.txt","w") as pwd_file:
                pwd_file.write(value)
            bot.send_message(message.chat.id,"Password Set!!!")
        elif(command.lower()=="name"):
            with open(folder_path+"name.txt","w") as name_file:
                name_file.write(value)
            bot.send_message(message.chat.id,"Name Set!!!")
    except Exception as e:
        print("Failed!!", e)




@bot.message_handler(commands=["pdf"])
def handle_pdf(message):
    try:
        os.mkdir(input_prefix+str(message.from_user.id))
    except:
        pass
    bot.set_state(message.from_user.id,MyStates.get_images,message.chat.id)

    bot.send_message(message.chat.id,"Bot Ready to recieve Images,\n\nTo add password to pdf use <code>password:12345</code>\n\nSend /create when ready",parse_mode="html")



@bot.message_handler(state=MyStates.got_image)
def utility_selector(message):
    # print(message.text)

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
    print(message.from_user.first_name+" compressed an Image")
    os.remove("input/temp.jpg")
    os.remove(output_path)
    bot.delete_state(message.from_user.id, message.chat.id)




@bot.message_handler(content_types=['photo'])
def image_receiver(message):
    

    reply_markup= ReplyKeyboardMarkup()
    reply_markup.add("Scanner","Compressor", row_width=2)

    bot.send_message(message.chat.id, "Image recieved", reply_markup=reply_markup)
    bot.set_state(message.from_user.id, MyStates.got_image, message.chat.id)
    # print("State Set")
    with bot.retrieve_data(message.from_user.id,message.chat.id) as data:
            data['file_id'] = message.photo[-1].file_id
    
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,"Hello There!!\nCurrent Features of the bot is:-\n1. Downsizing an Image to specified size\n2. Convert Image(s) to PDF")


bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.add_custom_filter(telebot.custom_filters.IsDigitFilter())

bot.infinity_polling()