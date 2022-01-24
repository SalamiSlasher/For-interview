import markups
import config
import MySQLdb
import dbApi

class Request:
    def __init__(self, bot, db, message=None, call=None, location=None):
        """
        :type bot: telebot.TeleBot
        """
        if location is not None:
            self.message = location
            self.latitude = self.message.location.latitude
            self.longitude = self.message.location.longitude
            self.user_id = self.message.from_user.id
        elif message is not None:
            self.message = message
            self.text = self.message.text
            self.user_id = self.message.from_user.id
            self.message_id = message.message_id
        elif call is not None:
            self.message = call.message
            self.data = call.data
            self.message_id = call.message.message_id
            self.user_id = call.from_user.id

        self.bot = bot
        self.chat_id = self.message.chat.id
        self.user_name = self.message.from_user.first_name
        self.db: dbApi.DbConnection = db

    def BasicHandler(self, f, debug):
        print('Class', id(self.db))

        try:
            ping = self.db.connection.ping()
        except MySQLdb._exceptions.OperationalError as e:
            print('-------------DB EXCEPT-------------')
            print(e)
            self.db.Reconnect()
            ping = self.db.connection.ping()

        print('ping', ping)

        if debug:
            f(self)
            return
        try:
            f(self)

        except BaseException as e:
            self.bot.send_message(477099094, str(e))
            self.bot.send_message(self.chat_id, 'Выберите нужную опцию или перезапустите бота командой /start')

    def EditMarkup(self, text, cmd):
        self.bot.edit_message_text(
            chat_id=self.chat_id, message_id=self.message_id,
            text=self.db.GetPhrase(text, self.user_id),
            reply_markup=markups.CreateMarkup(self.db, cmd, self.user_id))

    def SetLang(self):
        lang = self.data[8:]  # lang_Language
        self.db.SetLang(lang, self.user_id)
        self.EditMarkup('start', 'start')

    def ShowIllnessData(self):
        self.EditMarkup('ask_illness', 'illness_data')

    def ShowParagraphData(self):
        paragraph = self.data.split('_')[1]
        data, name = self.db.GetParagraphData(paragraph, self.user_id)
        flag_edit = True
        for content in data:
            if '&' in content:
                chat_id, msg_id = map(int, content.replace('\r\n', '')[1:].split(','))
                self.bot.forward_message(self.chat_id, chat_id, msg_id)
            else:
                if flag_edit:
                    self.bot.edit_message_text(
                        chat_id=self.chat_id, message_id=self.message_id, text=content, parse_mode="Markdown")
                    flag_edit = False
                else:
                    self.bot.send_message(self.chat_id, content)
        self.bot.reply_to(self.message, name)
        self.bot.send_message(
            self.chat_id,
            self.db.GetPhrase('read_continue', self.chat_id),
            reply_markup=markups.CreateMarkup(self.db, 'read_continue', self.user_id))

    def BackTo(self):
        self.db.SetState(self.user_id, '')
        cmd = self.data[5:]
        if cmd == 'lang':
            self.bot.edit_message_text(
                chat_id=self.chat_id, message_id=self.message_id,
                text=self.db.GetPhrase('back', self.user_id),
                reply_markup=markups.language_markup)
        else:
            self.EditMarkup('back', cmd)

    def AskOnline(self):
        self.bot.edit_message_text(
            chat_id=self.chat_id, message_id=self.message_id,
            text=self.db.GetPhrase('ask_online', self.user_id),
            reply_markup=markups.CreateMarkup(self.db, 'back_main', self.user_id))
        self.db.SetState(self.user_id, 'ask')

    def SendQuestion(self):
        if self.db.GetState(self.user_id) != 'ask':
            return
        id_ = self.db.AddMsg(self.message_id, self.message.text, self.chat_id)
        message = config.msg_form.format(id_, self.message.text)

        for i in config.superusers:
            self.bot.send_message(i, message)

        self.bot.send_message(self.chat_id, self.db.GetPhrase('ask_end', self.user_id),
                              reply_markup=markups.CreateMarkup(self.db, 'start', self.user_id))
        self.db.SetState(self.user_id, '')

    def AskQuestion(self):
        msg = self.message.text.split('\n')
        if len(msg) <= 1:
            return

        text = '\n'.join(msg[1:])
        try:
            id_ = int(msg[0].replace('/send ', ''))
            chat_id, msg_id = self.db.AnsMsg(id_, text)
            self.bot.send_message(chat_id, text, reply_to_message_id=msg_id)
            self.bot.send_message(chat_id, self.db.GetPhrase('start', self.user_id), reply_markup=markups.CreateMarkup(self.db, 'start', self.user_id))
            self.bot.send_message(self.chat_id, 'Ваше сообщение было отправлено')

        except:
            self.bot.send_message(self.chat_id, 'Отправьте сообщение в виде формы /send id\n*текст*. Первая строка обязана быть по форме')

    def CityInfo(self):
        lang = self.db.GetLang(self.user_id).lower()
        if lang == 'ru':
            text = config.tashkent_ru
        else:
            text = config.tashkent_uz

        self.bot.edit_message_text(
            chat_id=self.chat_id, message_id=self.message_id,
            text=text,
            reply_markup=markups.CreateMarkup(self.db, 'start', self.user_id))

    def StarHandler(self):
        markup, text = self.data[1:].split('_')
        self.bot.edit_message_text(
            chat_id=self.chat_id, message_id=self.message_id,
            text=text,
            reply_markup=markups.CreateMarkup(self.db, markup, self.user_id))
