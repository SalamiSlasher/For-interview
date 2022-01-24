import telebot
from dbApi import *
from templates import *
from config import debug
import os

try:
    os.chdir('mioma')
except FileNotFoundError:
    pass

bot = telebot.TeleBot(config.TOKEN)
db = DbConnection()

@bot.message_handler(commands=['start'])
def Welcome(message):
    try:
        bot.send_message(message.chat.id, 'Язык/Til', reply_markup=markups.language_markup)
    except BaseException as e:
        bot.send_message(477099094, str(e))
        bot.send_message(message.chat.id, 'Выберите нужную опцию или перезапустите бота командой /start')

@bot.message_handler(commands=['send'], func=lambda msg: msg.from_user.id in config.superusers)
def SendAns(message: telebot.types.Message):
    Request(bot, db, message=message).AskQuestion()

@bot.callback_query_handler(func=lambda call: call.data == 'ask_online')
def AskOnline(call):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['AskOnline'], debug)

@bot.message_handler(content_types=['text'])
def SendQuestion(message: telebot.types.Message):
    Request(bot, db, message=message).BasicHandler(Request.__dict__['SendQuestion'], debug)

@bot.callback_query_handler(func=lambda call: 'language' in call.data)
def SetLang(call: telebot.types.CallbackQuery):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['SetLang'], debug)

@bot.callback_query_handler(func=lambda call: 'illness' in call.data)
def ShowIllnessData(call: telebot.types.CallbackQuery):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['ShowIllnessData'], debug)

@bot.callback_query_handler(func=lambda call: 'paragraph' in call.data)
def ShowParagraphData(call):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['ShowParagraphData'], debug)

@bot.callback_query_handler(func=lambda call: 'back' in call.data)
def BackTo(call):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['BackTo'], debug)

@bot.callback_query_handler(func=lambda call: 'city' in call.data)
def CityInfo(call):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['CityInfo'], debug)

@bot.callback_query_handler(func=lambda call: call.data[0] == '*')
def StarHandler(call):
    Request(bot, db, call=call).BasicHandler(Request.__dict__['StarHandler'], debug)

@bot.callback_query_handler(func=lambda call: True)
def fek(call):
    bot.send_message(call.message.chat.id, 'Выберите нужную опцию или перезапустите бота командой /start')

@bot.message_handler(content_types=['text'], func=lambda msg: '$2281337$' in msg.text)
def GodMode(message):
    """
    :type message: telebot.types.Message
    """
    msg = message.text.split(config.god_mode)[1]
    if msg == 'id':
        print(message.message_id, message.chat.id)
    elif 'fwd' in msg:
        print(message.chat.id)
        bot.forward_message(message.chat.id, 1894506481, 1486)

if __name__ == '__main__':
    bot.polling(none_stop=True)
