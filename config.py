import datetime

host = '127.0.0.1'
port = 8001
server_debug = True

db = 'sqlite:///db.sqlite'
sql_debug = False
token_length = 16
secret_length = 16

semester_end = [
    datetime.date(2015, 2, 15),
    datetime.date(2015, 9, 13),
    datetime.date(2016, 2, 21),
    datetime.date(2016, 9, 18)
]

shared_secret = 'VERYSECUREPASSPHRASE'
