import sshtunnel
import MySQLdb
import config

class DbConnection:
    tunnel = None
    connection = None
    cursor = None

    def __init__(self):
        self.reconnect()

    def reconnect(self):
        try:
            self.connection.ping()
        except BaseException as e:
            self.tunnel = sshtunnel.SSHTunnelForwarder(
                config.db_url, **config.db_tunnel)
            self.tunnel.start()
            self.connection = MySQLdb.connect(
                **config.db_connection, port=self.tunnel.local_bind_port)
            self.cursor = self.connection.cursor()

    def add_user(self, userid, name):
        self.cursor.execute("SELECT id FROM UserData WHERE id = {}".format(userid))
        data = self.cursor.fetchall()
        if len(data) == 0:
            self.cursor.execute("INSERT INTO UserData (id, name, state, stack) VALUES ({}, '{}', 'main', '')".format(userid, name))
        else:
            self.cursor.execute("UPDATE UserData SET state = 'main', stack = '' WHERE id = {}".format(userid))
        self.connection.commit()

    def get_state(self, userid):
        self.cursor.execute("SELECT state FROM UserData WHERE id = {}".format(userid))
        return self.cursor.fetchone()[0]

    def set_state(self, userid, state):
        self.cursor.execute("UPDATE UserData SET state = '{}' WHERE id = {}".format(state, userid))
        self.connection.commit()

    def get_stack(self, userid):
        self.cursor.execute("SELECT stack FROM UserData WHERE id = {}".format(userid))
        return self.cursor.fetchone()[0]

    def set_stack(self, userid, stack):
        self.cursor.execute("UPDATE UserData SET stack = '{}' WHERE id = {}".format(stack, userid))
        self.connection.commit()

    def add_client(self, data):
        self.cursor.execute("SELECT * FROM CRM WHERE (id, city, lpu, address, doc, contacts) = ('{id}', '{city}', "
                            "'{lpu}', '{address}', '{doc}', '{contacts}')".format(**data))
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute("INSERT INTO CRM VALUES ('{id}', '{city}', '{lpu}', '{address}', '{doc}', "
                                "'{contacts}', '', '', '')".format(**data))
        self.connection.commit()

    def manager_data(self, userid):
        self.cursor.execute("SELECT city, lpu, address, doc, contacts, data, location, data_id FROM CRM WHERE id = {}".format(userid))
        return self.cursor.fetchall()

    def add_data(self, data):
        self.cursor.execute("SELECT data, location FROM CRM WHERE data_id = {}".format(data['data_id']))
        cursor = self.cursor.fetchone()
        text = '\n~\n'.join((cursor[0], data['text']))
        location = '\n~\n'.join((cursor[1], data['location']))
        self.cursor.execute("UPDATE CRM SET data = '{}', location = '{}' WHERE data_id = {}".format(
            text, location, data['data_id']))
        self.connection.commit()

    def get_data(self):
        self.cursor.execute("SELECT * FROM CRM")
        return self.cursor.fetchall()

    def get_name(self, id_):
        self.cursor.execute("SELECT name FROM UserData WHERE id = {}".format(id_))
        return self.cursor.fetchone()[0]
