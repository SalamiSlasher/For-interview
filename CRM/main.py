import telebot
import config
import dbAPI
from handler import Handler, msg_graph
import phrases

bot = telebot.TeleBot(config.TOKEN)
db = dbAPI.DbConnection()
print('===========connected===========')


@bot.message_handler(commands=['start'])
def welcome(message: telebot.types.Message):
    Handler(bot, db, msg=message).basic_handler(Handler.__dict__['welcome'])


@bot.callback_query_handler(func=lambda call: True)
def basic_callback_handler(call: telebot.types.CallbackQuery):
    if 'redact' in call.data:
        Handler(bot, db, call=call).basic_handler(Handler.__dict__['redact'])
        return
    if 'visit_new_' in call.data:
        Handler(bot, db, call=call).basic_handler(Handler.__dict__['visit_new'])
        return
    if call.data not in Handler.__dict__:
        return
    Handler(bot, db, call=call).basic_handler(Handler.__dict__[call.data])


@bot.message_handler(content_types=['text'], func=lambda msg: True)
def add_basic(message: telebot.types.Message):
    raw_state = db.get_state(message.from_user.id)
    state = raw_state.split('_')

    if len(state) < 2:
        return

    if state[0] in ('add', 'redact') and state[0]:
        Handler(bot, db, msg=message).basic_handler(Handler.__dict__[state[0] + '_basic'])
    elif raw_state == 'visit_description':
        print('hwwa')
        Handler(bot, db, msg=message).basic_handler(Handler.__dict__['visit_description'])


@bot.message_handler(content_types=['location'])
def get_location(location):
    Handler(bot, db, location=location).basic_handler(Handler.__dict__['visit_geo'])


if __name__ == '__main__':
    bot.polling(none_stop=True)
