import MySQLdb
import sshtunnel
import config

class DbConnection:
    tunnel = None
    connection = None
    cursor = None

    def __init__(self):
        self.Reconnect()

    def Reconnect(self):
        self.tunnel = sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'), **config.db_tunnel)
        self.tunnel.start()
        self.connection = MySQLdb.connect(
            **config.db_connection, port=self.tunnel.local_bind_port)
        self.cursor = self.connection.cursor()

    def SetLang(self, lang, user_id):
        self.cursor.execute("SELECT userid FROM UserData WHERE userid = {id}".format(id=user_id))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("INSERT INTO UserData (userid, lang) VALUES ({id}, '{lang}')".format(
                id=user_id, lang=lang))
        else:
            self.cursor.execute("UPDATE UserData SET lang = '{lang}' WHERE userid = {id}".format(
                id=user_id, lang=lang))
        self.connection.commit()

    def GetLang(self, user_id):
        self.cursor.execute("SELECT lang FROM UserData WHERE userid = {id}".format(id=user_id))
        return self.cursor.fetchone()[0]

    def GetPhrase(self, cmd, user_id):
        lang = self.GetLang(user_id)
        self.cursor.execute("SELECT {} FROM Phrases WHERE phrase = '{}'".format(lang, cmd))
        return self.cursor.fetchone()[0]

    def GetParagraphData(self, paragraph, user_id):
        lang = self.GetLang(user_id)
        self.cursor.execute("SELECT {}, translate FROM Content WHERE content = '{}'".format(lang, paragraph))
        text, translate = self.cursor.fetchone()
        for i in translate.split('\r\n'):
            lang_, name = i.split('_')
            if lang_ == lang:
                return text.split('~'), name

    def GetState(self, user_id):
        self.cursor.execute("SELECT state FROM UserData WHERE userid = {}".format(user_id))
        return self.cursor.fetchone()[0]

    def SetState(self, id_, state):
        self.cursor.execute("UPDATE UserData SET state = '{}' WHERE userid = {}".format(state, id_))
        self.connection.commit()

    def GetMarkupData(self, cmd, user_id):
        lang = self.GetLang(user_id)
        self.cursor.execute("SELECT * FROM Markups WHERE lang = '{}' AND markup = '{}'".format(lang, cmd))
        data = self.cursor.fetchone()
        return data[2].split('\r\n'), data[3].split('\r\n')  # [text_1...text_i], [callback_1...callback_i]

    def AddMsg(self, msg_id, text, userid):
        self.cursor.execute(
            "INSERT INTO Questions (msg_id, msg, userid) VALUES  ('{}', '{}', '{}')".format(msg_id, text, userid))
        self.connection.commit()
        return self.cursor.lastrowid

    def AnsMsg(self, id_, text):
        self.cursor.execute("UPDATE Questions SET msg_ans = '{}' WHERE id = {}".format(text, id_))
        self.cursor.execute("SELECT userid, msg_id FROM Questions WHERE id = {}".format(id_))
        self.connection.commit()
        return self.cursor.fetchone()

    def __del__(self):
        self.tunnel.close()
        self.connection.close()
