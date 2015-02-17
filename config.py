import datetime

webui_host = '127.0.0.1'
webui_port = 8001

api_host = '127.0.0.1'
api_port = 8003

flash_device = 1

server_debug = True

db = 'sqlite:///db.sqlite'
sql_debug = False
token_length = 16
secret_length = 16

server_token = 'ASDFGHJKL1029384'
webui_token = '1029384ASDFGHJKL'

semester_end = [
    datetime.date(2015, 2, 15),
    datetime.date(2015, 9, 13),
    datetime.date(2016, 2, 21),
    datetime.date(2016, 9, 18)
]

shared_secret = 'VERYSECUREPASSPHRASE'

ping_interval = 30
pong_interval = 30