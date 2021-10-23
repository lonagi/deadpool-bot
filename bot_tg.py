#!/usr/bin/env python
# coding: utf-8
from telebot import types
import telebot
import requests as req
import datetime, re, json, os, json


try:
    import nvgconfg
    nvgconfgtoken = nvgconfg.token
except:
    pass
bot = telebot.TeleBot(nvgconfgtoken)

MAIN_PATH = "/mnt/dav/Music"
    
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
    ccs = ("/music", '/pulse', '/mount', '/kill',)
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
    
@bot.message_handler(commands=['kill'])
def kill(message):
    c = "kill"
    os.system(c)
    bot.send_message(message.chat.id, f"$ {c}")

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
            c = f"pulseaudio -D & mpg321 {j[1]}/{file} -K -v -l 0 -g 10"
            os.system(c)
            
bot.polling(none_stop=True)
