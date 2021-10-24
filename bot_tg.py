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
    ADMIN = nvgconfg.admin
    API_URL = nvgconfg.api
except:
    pass

MAIN_PATH = "/mnt/dav/Music"
bot = telebot.TeleBot(nvgconfgtoken)

def add_stat(htype, value):
    req.post(f"{API_URL}/deadpool/entry.php", data={"htype":htype, "value":value})

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
    
    if folder:
        fpath = f"{folder}/{file}"
    else:
        fpath = f"{file}"
    fpath = fpath.replace("\ "," ").replace("\&","&")
    
    #bot.send_message(message.chat.id, c, reply_markup=markup)
    bot.send_message(message.chat.id, f"Включаю {fpath}", reply_markup=markup)
    __kill()
    os.system(c)

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
        
    for page in range(1,len(mm)//50+2):
        keyboard = types.InlineKeyboardMarkup()
        p = 0
        for i in mm[(page-1)*50:page*50+1]:
            if pref == "j":
                callback_button = types.InlineKeyboardButton(text=str(i), callback_data=f"{pref}{json.dumps([p,page,path])}")
            elif pref == "i":
                callback_button = types.InlineKeyboardButton(text=str(i), callback_data=f"{pref}{i}")
            keyboard.add(callback_button)
            p += 1
        bot.send_message(message.chat.id, m, reply_markup=keyboard)
        time.sleep(1)
    
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
        add_stat("mount","dav")
        bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['pulse'])
def pulse(message):
    if ADMIN == str(message.chat.id):
        c = "pulseaudio -D"
        os.system(c)
        add_stat("pulse","-D")
        bot.send_message(message.chat.id, f"$ {c}")
        
@bot.message_handler(commands=['play'])
def play(message):
    if ADMIN == str(message.chat.id):
        m = message.text.split(" ")
        if len(m) > 1:
            m = " ".join(m[1:]).replace(" ","\ ").replace("&","\&")
            add_stat("music_play_play",m)
            playfile(message, None, m)
        else:
            add_stat("music_play_error","play")
            bot.send_message(message.chat.id, f"Нет такого файла")

def __find(message):
    m = message.text.split(" ")
    if len(m) > 1:
        m = " ".join(m[1:]).replace(" ","\ ").replace("&","\&")
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "Ищу музыку...", reply_markup=markup)

        s = get_all_music()
        song = process.extractOne(m,s)
        add_stat("music_play_find",m)
        playfile(message, None, song[0].replace(" ","\ ").replace("&","\&"))
    else:
        add_stat("music_play_error","find")
        bot.send_message(message.chat.id, f"Нет такого пути")
            
@bot.message_handler(commands=['find'])
def find(message):
    if ADMIN == str(message.chat.id):
        __find(message)
        
@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    if ADMIN == str(message.chat.id):
        c = "shutdown"
        os.system(c)
        add_stat("shutdown","berry")
        bot.send_message(message.chat.id, f"$ {c}")
    
@bot.message_handler(commands=['reboot'])
def reboot(message):
    if ADMIN == str(message.chat.id):
        c = "reboot"
        os.system(c)
        add_stat("reboot","berry")
        bot.send_message(message.chat.id, f"$ {c}")
        
def __kill():
    pids = get_proc()
    if pids:
        for pid in pids:
            os.system(f"kill {pid}")
    
@bot.message_handler(commands=['kill','stop','стоп'])
def kill(message):
    if ADMIN == str(message.chat.id):
        add_stat("music_stop","stop")
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
            add_stat("music_volume",m)
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
            add_stat("music_loop",m)
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
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id, timeout=None)
                navigate(bot, call.message, f"{MAIN_PATH}/{f}", "j")
            elif call.data[0] == "j":
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id, timeout=None)
                
                j = json.loads(call.data[1:])
                f,d,s = [],[],[]
                for (dirpath, dirnames, filenames) in os.walk(j[2]):
                    d.extend(dirpath)
                    f.extend(dirnames)
                    s.extend(filenames)
                    break
                file = s[50*(j[1]-1)+j[0]].replace(" ","\ ").replace("&","\&")
                add_stat("music_play_nav", f"{j[2]}/{file}")
                playfile(call.message, j[2], file)

@bot.message_handler(content_types=['text'])
def siri_find(message):
    if ADMIN == str(message.chat.id):
        if message.text.split(" ")[0] in ("Найди", "Включи", "Включаю", "Вруби"):
            __find(message)
            
bot.polling(none_stop=True)
