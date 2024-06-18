import telebot
import os
from Detector import DocScan
import requests
import cv2

token = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['photo'])
def image_receiver(message):
    file = bot.get_file(message.photo[-1].file_id)
    # print(file)
    
    response= requests.get(f"https://api.telegram.org/file/bot{token}/{file.file_path}")
    with open("input/temp.jpg","wb") as f:
        f.write(response.content)
    
    image = cv2.imread("input/temp.jpg")
    scanner = DocScan(final_output=True,output=True)
    image, dest = scanner.scan(image)
    bot.send_photo(message.chat.id, open(dest,"rb"))

    os.remove("input/temp.jpg")
    os.remove(dest)

bot.infinity_polling()