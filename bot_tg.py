#!/usr/bin/env python
# coding: utf-8
from telebot import types
from fuzzywuzzy import process
import keyboard
import telebot
import requests as req
import datetime, re, json, os, json, time


try:
    import nvgconfg
    nvgconfgtoken = nvgconfg.token
except:
    pass

MAIN_PATH = "/mnt/dav/Music"
ADMIN = ""
bot = telebot.TeleBot(nvgconfgtoken)

def get_proc():
    stream_cmd = os.popen("pgrep -f mpg321")
    response = stream_cmd.read()
    response = [i for i in response.split('\n') if i != '']
    return response

def get_stop_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    ccs = ('/stop',)
    for i in ccs:
        itembtn = types.KeyboardButton(i)
        markup.add(itembtn)
    return markup

def runfile(folder, file):
    with open("./volume.txt","r") as f:
        getvolume=int(f.read())
    with open("./loops.txt","r") as f:
        loops=int(f.read())
    if folder:
        fpath = f"{folder}/{file}"
    else:
        fpath = f"{file}"
    return f"pulseaudio -D & mpg321 {fpath} -K -v -l {loops} -g {getvolume} --stereo"

def playfile(message, folder, file):
    markup = get_stop_markup()
    c = runfile(folder, file)
    os.system(c)
    
    if folder:
        fpath = f"{folder}/{file}"
    else:
        fpath = f"{file}"
    fpath = fpath.replace("\ "," ")
    
    #bot.send_message(message.chat.id, c, reply_markup=markup)
    bot.send_message(message.chat.id, f"Включаю {fpath}", reply_markup=markup)

def get_all_music():
    s = []
    for (_, dirnames, _) in os.walk(MAIN_PATH):
        for d in dirnames:
            for (_, _, filenames) in os.walk(f"{MAIN_PATH}/{d}"):
                for f in filenames:
                    s.append(f"{MAIN_PATH}/{d}/{f}")
                break
        break
    return s
    
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
    if ADMIN == str(message.chat.id):
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        ccs = ("/music", '/loop', '/volume', '/stop', '/pulse', '/mount')
        for i in ccs:
            itembtn = types.KeyboardButton(i)
            markup.add(itembtn)
        bot.send_message(message.chat.id, "Выбери команду", reply_markup=markup)
    
@bot.message_handler(commands=['mount'])
def mount(message):
    if ADMIN == str(message.chat.id):
        c = "mount /mnt/dav"
        os.system(c)
        bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['pulse'])
def pulse(message):
    if ADMIN == str(message.chat.id):
        c = "pulseaudio -D"
        os.system(c)
        bot.send_message(message.chat.id, f"$ {c}")
        
@bot.message_handler(commands=['play'])
def play(message):
    if ADMIN == str(message.chat.id):
        m = message.text.split(" ")
        if len(m) > 1:
            m = m[-1].replace(" ","\ ")
            playfile(message, None, m)
        else:
            bot.send_message(message.chat.id, f"Нет такого файла")

@bot.message_handler(commands=['find'])
def find(message):
    if ADMIN == str(message.chat.id):
        m = message.text.split(" ")
        if len(m) > 1:
            m = m[-1]
            s = get_all_music()
            print(s)
            song = process.extractOne(m,s)
            playfile(message, None, song)
        else:
            bot.send_message(message.chat.id, f"Нет такого пути")
        
@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    if ADMIN == str(message.chat.id):
        c = "shutdown"
        os.system(c)
        bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['reboot'])
def reboot(message):
    if ADMIN == str(message.chat.id):
        c = "reboot"
        os.system(c)
        bot.send_message(message.chat.id, f"$ {c}")
        
def __kill():
    pids = get_proc()
    if pids:
        for pid in pids:
            os.system(f"убиваю процесс {pid}")
    
@bot.message_handler(commands=['kill','stop','стоп'])
def kill(message):
    if ADMIN == str(message.chat.id):
        __kill()
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Стоп", reply_markup=markup)
    
@bot.message_handler(commands=['volume',"громкость"])
def volume(message):
    if ADMIN == str(message.chat.id):
        m = message.text.split(" ")
        if len(m) > 1:
            m = m[-1]
            with open("./volume.txt","w") as f:
                f.write(m)
            bot.send_message(message.chat.id, f"Ок")
        else:
            bot.send_message(message.chat.id, f"Например /volume 50")

@bot.message_handler(commands=['loop',"повтор"])
def loops(message):
    if ADMIN == str(message.chat.id):
        m = message.text.split(" ")
        if len(m) > 1:
            m = m[-1]
            with open("./loops.txt","w") as f:
                f.write(m)
            bot.send_message(message.chat.id, f"Ок")
        else:
            bot.send_message(message.chat.id, f"Например /loop 3")

@bot.message_handler(commands=['music','музыка','m',"м"])
def music(message):
    if ADMIN == str(message.chat.id):
        navigate(bot, message, MAIN_PATH)
    
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if ADMIN == str(call.message.chat.id):
        if call.message:
            if call.data[0] == "i":
                f = call.data[1:]
                chat_id=call.message.chat.id, message_id=call.message.message_id
                navigate(bot, call.message, f"{MAIN_PATH}/{f}", "j")
            elif call.data[0] == "j":
                __kill()
                markup = get_stop_markup()
                bot.send_message(call.message.chat.id, "Включаю...", reply_markup=markup)
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id, timeout=None)
                
                j = json.loads(call.data[1:])
                f,d,s = [],[],[]
                for (dirpath, dirnames, filenames) in os.walk(j[1]):
                    d.extend(dirpath)
                    f.extend(dirnames)
                    s.extend(filenames)
                    break
                file = s[j[0]].replace(" ","\ ")
                playfile(call.message, j[1], file)
            
bot.polling(none_stop=True)
