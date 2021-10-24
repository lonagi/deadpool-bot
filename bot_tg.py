#!/usr/bin/env python
# coding: utf-8
from telebot import types
import keyboard
import telebot
import requests as req
import datetime, re, json, os, json, time


try:
    import nvgconfg
    nvgconfgtoken = nvgconfg.token
except:
    pass
bot = telebot.TeleBot(nvgconfgtoken)

MAIN_PATH = "/mnt/dav/Music"

def get_proc():
    stream_cmd = os.popen("pgrep -f mpg321")
    response = stream_cmd.read()
    response = [i for i in response.split('\n') if i != '']
    return response
    
def navigate(bot, message, path, pref = "i"):
    f,d,s = [],[],[]
    for (dirpath, dirnames, filenames) in os.walk(path):
        d.extend(dirpath)
        f.extend(dirnames)
        s.extend(filenames)
        break
    
    if pref == "i":
        m = "Выбери папку"
        mm = f
    else:
        m = "Выбери файл"
        mm = s
        
    keyboard = types.InlineKeyboardMarkup()
    p = 0
    for i in mm:
        if pref == "j":
            callback_button = types.InlineKeyboardButton(text=str(i), callback_data=f"{pref}{json.dumps([p,path])}")
        elif pref == "i":
            callback_button = types.InlineKeyboardButton(text=str(i), callback_data=f"{pref}{i}")
        keyboard.add(callback_button)
        p += 1
    bot.send_message(message.chat.id, m, reply_markup=keyboard)
    
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    ccs = ("/music", '/loop', '/volume', '/stop', '/pulse', '/mount')
    for i in ccs:
        itembtn = types.KeyboardButton(i)
        markup.add(itembtn)
    bot.send_message(message.chat.id, "Выбери команду", reply_markup=markup)
    
@bot.message_handler(commands=['mount'])
def mount(message):
    c = "mount /mnt/dav"
    os.system(c)
    bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['pulse'])
def pulse(message):
    c = "pulseaudio -D"
    os.system(c)
    bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['kill','stop','стоп'])
def kill(message):
    pids = get_proc()
    if pids:
        for pid in pids:
            os.system(f"kill {pid}")
    bot.send_message(message.chat.id, f"Stop")

@bot.message_handler(commands=['music','музыка','m',"м"])
def music(message):    
    navigate(bot, message, MAIN_PATH)
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data[0] == "i":
            f = call.data[1:]
            navigate(bot, call.message, f"{MAIN_PATH}/{f}", "j")
        elif call.data[0] == "j":
            j = json.loads(call.data[1:])
            f,d,s = [],[],[]
            for (dirpath, dirnames, filenames) in os.walk(j[1]):
                d.extend(dirpath)
                f.extend(dirnames)
                s.extend(filenames)
                break
            file = s[j[0]].replace(" ","\ ")
            with open("./volume.txt","r") as f:
                getvolume=int(f.read())
            with open("./loops.txt","r") as f:
                loops=int(f.read())
            c = f"pulseaudio -D & mpg321 {j[1]}/{file} -K -v -l {loops} -g {getvolume} --stereo"
            os.system(c)
            bot.send_message(call.message.chat.id, c)
            
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            ccs = ('/stop',)
            for i in ccs:
                itembtn = types.KeyboardButton(i)
                markup.add(itembtn)
            bot.send_message(message.chat.id, "Управляй", reply_markup=markup)
            
bot.polling(none_stop=True)
