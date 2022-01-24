import os

debug = True
superusers = [1126203631, 132522885]
god_mode = '$2281337$'

TOKEN = os.environ.get('token')

# ================== WILL USE ENV VARIABLES! ==================
db_tunnel = {
    'ssh_username': os.environ.get('ssh_user'),
    'ssh_password': os.environ.get('ssh_pass'),
    'remote_bind_address': (os.environ.get('bind'), 3306)
}
db_connection = {
    'user': os.environ.get('user'),
    'passwd': os.environ.get('pass'),
    'host': '127.0.0.1',
    'db': os.environ.get('db_name')
}


msg_form = """id: #{}

{}
"""

# ================== WILL FIX ==================
tashkent_ru = """Республиканский научно-практический медицинский центр терапии и медицинской реабилитации (бывший санаторий Семашко)

Исхаков Шерзод Алишерович
+998 90 943 48 36

Каюмов Нодир Улугбекович
+998 90-909-99-90
"""

tashkent_uz = """Ташкент Республика ихтисослаштирилган терапия ва тиббий реабилитация илмий-амалий тиббиёт маркази (собиқ Семашко номидаги санаторий).

Исхаков Шерзод Алишерович
+998 90 943 48 36

Каюмов Нодир Улугбекович

+998 90-909-99-90
"""
# ================== WILL FIX ==================
