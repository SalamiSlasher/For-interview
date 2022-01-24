from telebot import types

language_markup = types.InlineKeyboardMarkup()
language_markup.add(types.InlineKeyboardButton('🇺🇿', callback_data='languageUz'))
language_markup.add(types.InlineKeyboardButton('🇷🇺', callback_data='languageRu'))

def CreateMarkup(db, cmd, user_id):
    markup = types.InlineKeyboardMarkup()
    data = db.GetMarkupData(cmd, user_id)
    for i in range(len(data[0])):
        markup.add(types.InlineKeyboardButton(
            text=data[0][i], callback_data=data[1][i]))
    return markup
