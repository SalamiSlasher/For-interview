import dbAPI
import telebot
import config
import phrases
from telebot import types
import datetime
import pandas

markups = {
    'welcome': (('Добавить запись', 'Поспотреть записи'), ('add_start', 'show_admin')),
    'add_start': (('Добавить нового клиента', 'добавить новый визит', 'Вернуться в главное меню'),
                  ('add_client', 'visit_show', 'back_main')),
    'back_main': (['Вернуться в главное меню'], ['back_main']),
    'add_check': ((
                      'Подтвердить и добавить клиента✅', 'Изменить город', 'Изменить ЛПУ', 'Изменить адрес',
                      'Изменить ФИО',
                      'Изменить контакты', 'Вернуться в главное меню'),
                  ('add_confirm', 'redact_city', 'redact_lpu', 'redact_address', 'redact_doc', 'redact_contacts',
                   'back_main')),
    'visit_new': [['Добавить новый визит'], ['visit_new_{msg_id}_{data_id}']],
    'confirm_data': (('Подтвердить данные ✅', 'Изменить данные', 'Вернуться в главное меню'),
                     ('data_geo', 'data_change', 'back_main'))
}

msg_graph = {
    'add_city': 'add_lpu',
    'add_lpu': 'add_address',
    'add_address': 'add_doc',
    'add_doc': 'add_contacts',
    'add_contacts': 'add_check',
}


def basic_markup(text: tuple, callback: list):
    if len(text) != len(callback):
        raise ValueError("len(text) != len(callback_data)")
    markup = types.InlineKeyboardMarkup()
    for i in range(len(text)):
        markup.add(types.InlineKeyboardButton(text[i], callback_data=callback[i]))
    return markup


class Handler:
    def __init__(self, bot, db, msg=None, call=None, location=None):
        """
        :type db: dbAPI.DbConnection
        :type bot: telebot.TeleBot
        :type msg: telebot.types.Message
        :type call: telebot.types.CallbackQuery
        :type location: telebot.types.Message
        """
        self.bot = bot
        self.db = db
        self.message = msg

        if call is not None:
            self.message = call.message
            self.data = call.data
        elif location is not None:
            self.message = location
            self.latitude = self.message.location.latitude
            self.longitude = self.message.location.longitude

        self.text = self.message.text
        self.user_id = self.message.from_user.id if call is None else call.from_user.id
        self.message_id = self.message.message_id
        self.name, self.surname = map(str, (self.message.from_user.first_name, self.message.from_user.last_name))
        self.chat_id = self.message.chat.id

    def basic_handler(self, f):
        if config.debug:
            f(self)
            return
        try:
            f(self)
        except BaseException as e:
            self.bot.send_message(477099094, str(e))
            self.bot.send_message(self.chat_id, 'Выберите нужную опцию или перезапустите бота командой /start')

    def welcome(self):
        username = ' '.join((self.name, self.surname))
        self.db.add_user(self.user_id, username)
        self.db.set_stack(self.user_id, '')
        with open('Руководство по работе с CRM ботом.pdf', 'rb') as f:
            pass
            # self.bot.send_document(self.chat_id, f)
        self.bot.send_message(self.chat_id, phrases.welcome,
                              reply_markup=basic_markup(*markups['welcome']))

    def markups_jumper(self, needed_state, new_state, msg_text, markup, stack=None, send=False, reply=None):
        if self.db.get_state(self.user_id) != needed_state and needed_state != 'back_main':
            return
        if send:
            self.bot.send_message(self.chat_id, msg_text,
                                  reply_markup=basic_markup(*markups[markup]), reply_to_message_id=reply)
        else:
            self.bot.edit_message_text(text=msg_text, chat_id=self.chat_id,
                                       message_id=self.message_id, reply_markup=basic_markup(*markups[markup]))
        self.db.set_state(self.user_id, new_state)
        if stack is not None:
            self.db.set_stack(self.user_id, stack)

    def add_basic(self):
        state, stack = self.db.get_state(self.user_id), self.db.get_stack(self.user_id)
        #  TO FIX :\
        if state in ('add_client', 'add_check', 'add_confirm', 'redact_address'):
            return
        new_stack = '\n~\n'.join((stack, self.text))
        new_state = msg_graph[state]
        self.db.set_stack(self.user_id, new_stack)
        self.db.set_state(self.user_id, new_state)
        if new_state != 'add_check':
            self.bot.send_message(self.chat_id, phrases.add[new_state][0],
                                  reply_markup=basic_markup(*markups['back_main']))
        else:
            text = phrases.check_info.format(*new_stack.split('\n~\n')[1:])
            self.markups_jumper(new_state, new_state, text, 'add_check', send=True)

    def redact_basic(self):
        stack, state = self.db.get_stack(self.user_id).split('\n~\n'), self.db.get_state(self.user_id)
        #  зафиксить :\
        index = phrases.add['add_' + state.split('_')[1]][1]
        stack[index] = self.text
        self.db.set_stack(self.user_id, '\n~\n'.join(stack))
        text = phrases.check_info.format(*stack[1:])
        self.markups_jumper(state, 'add_check', text, 'add_check', send=True)

    def add_start(self):
        self.markups_jumper('main', 'add_client', phrases.option, 'add_start')

    def add_client(self):
        self.markups_jumper('add_client', 'add_city', phrases.add['add_city'][0], 'back_main')

    def add_confirm(self):
        stack = self.db.get_stack(self.user_id).split('\n~\n')
        data = {
            'id': self.user_id,
            'city': stack[1],
            'lpu': stack[2],
            'address': stack[3],
            'doc': stack[4],
            'contacts': stack[5],
        }
        self.db.add_client(data)
        self.markups_jumper('back_main', 'add_client', phrases.add_confirm, 'add_start')
        self.db.set_stack(self.user_id, '')

    def redact(self):
        phrase = phrases.add['add' + '_' + self.data.split('_')[1]][0]
        self.markups_jumper('add_check', self.data, phrase, 'back_main')

    def visit_show(self):
        if self.db.get_state(self.user_id) != 'add_client':
            return
        manager_data = self.db.manager_data(self.user_id)
        #msg = self.bot.edit_message_text(text=phrases.show_clients, chat_id=self.chat_id,
        #                                 message_id=self.message_id)
        msg = self.bot.send_message(self.chat_id, phrases.show_clients)
        for i in range(len(manager_data)):
            city, lpu, address, doc, contacts, data, location, data_id = manager_data[i]
            data = data.split('\n~\n')
            text = phrases.client_info.format(city, lpu, address, doc, contacts) + '\n\n'.join(data)
            mk_text, callback = markups['visit_new'][0], markups['visit_new'][1].copy()
            callback[0] = callback[0].format(msg_id=msg.message_id + i + 1, data_id=data_id)
            #markup[1][0] = markup[1][0].format(msg_id=msg.message_id + i + 1, data_id=data_id)
            markup = basic_markup(mk_text, callback)
            kek = self.bot.send_message(self.chat_id, text, reply_markup=markup)
        self.bot.send_message(self.chat_id, phrases.back_text,
                              reply_markup=basic_markup(*markups['back_main']), reply_to_message_id=msg.id)
        self.db.set_state(self.user_id, 'visit_show')

    def visit_new(self):
        state = self.db.get_state(self.user_id)
        if state not in ('visit_show', 'visit_check'):
            return
        data = self.data.split('_')
        if len(data) == 4:
            msg_id, data_id = self.data.split('_')[2:]
        else:
            msg_id, data_id = None, self.db.get_stack(self.user_id).split('\n~\n')[0]
        self.markups_jumper(state, 'visit_description', phrases.add['visit_description'],
                            'back_main', stack=data_id, send=True, reply=msg_id)

    def visit_description(self):
        if self.db.get_state(self.user_id) != 'visit_description':
            return

        stack = '\n~\n'.join((self.db.get_stack(self.user_id), self.text))
        self.markups_jumper('visit_description', 'visit_check', phrases.check_data.format(self.text),
                            'confirm_data', stack=stack, send=True)

    def data_change(self):
        self.visit_new()

    def data_geo(self):
        self.markups_jumper('visit_check', 'visit_geo', phrases.ask_geo, 'back_main', send=True)

    def visit_geo(self):
        if self.db.get_state(self.user_id) != 'visit_geo':
            return
        l = self.message.json['location']
        if 'live_period' in self.message.json['location']:
            location = '_'.join((str(l['latitude']), str(l['longitude'])))
            data_id, text = self.db.get_stack(self.user_id).split('\n~\n')
            data = {
                'data_id': data_id,
                'text': datetime.datetime.strftime(datetime.datetime.now(), '%x %X') + '\n' + text,
                'location': location
            }
            self.db.add_data(data)
            self.bot.send_message(self.chat_id, phrases.data_confirm)
            self.welcome()
        else:
            self.bot.send_message(self.chat_id, phrases.incorrect_geo)

    def show_admin(self):
        if self.user_id not in config.admins:
            self.bot.send_message(self.chat_id, phrases.permission_denied)
            return
        df = {
            'Менеджер': [],
            'Город': [],
            'ЛПУ': [],
            'Адрес ЛПУ': [],
            'ФИО врача': [],
            'Контакты врача': []
        }
        data = self.db.get_data()
        for i in range(len(data)):
            df['Менеджер'].append(self.db.get_name(data[i][0]))
            df['Город'].append(data[i][1]),
            df['ЛПУ'].append(data[i][2]),
            df['Адрес ЛПУ'].append(data[i][3]),
            df['ФИО врача'].append(data[i][4]),
            df['Контакты врача'].append(data[i][5]),
            if data[i][6] != '':
                text = data[i][6].split('\n~\n')[1:]
                location = data[i][7].split('\n~\n')[1:]
                for j in range(len(text)):
                    vis = 'Визит {}'.format(j + 1)
                    loc = 'Геолокация {}'.format(j + 1)
                    if vis not in df:
                        df[vis] = [''] * len(data)
                        df[loc] = [''] * len(data)
                    df[vis][i] = text[j]
                    df[loc][i] = 'https://maps.google.com/?q={},{}'.format(*location[j].split('_'))

        df = pandas.DataFrame(df)
        df.to_excel('./Отчет.xlsx', index=False)
        with open('./Отчет.xlsx', 'rb') as doc:
            self.bot.send_document(self.chat_id, doc)
        self.welcome()

    def back_main(self):
        self.markups_jumper('back_main', 'main', phrases.back_main, 'welcome', stack='', send=True)
