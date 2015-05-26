import json

# ------------- CONSTANT ----------------

webui_host = '127.0.0.1'
webui_port = 8001

api_host = '129.132.17.47'
api_port = 8003

server_debug = True

service_path = 'services/'

db = 'sqlite:///db.sqlite'
sql_debug = False

token_length = 16
secret_length = 16

# Keep this very secret
webui_sessions_secret = 'adsjkfhasdjkfhjkasdhfkasdjhfkloajshdfjskdf'

ping_interval = 30
pong_interval = 30

# ------------- READONLY -----------------

webui_token = '1029384ASDFGHJKL'

server_token = 'ASDFGHJKL1029384'

api_token = 'VERYSECUREPASSPHRASE'

# ------------- CUSTO)M ------------------


def read_config(key, default=None):
    data_default = open('config/config_default.json')
    conf_default = json.loads(data_default.read())
    data_default.close()

    data_custom = open('config/config_custom.json')
    conf_custom = json.loads(data_custom.read())
    data_custom.close()

    if key in conf_custom:
        return conf_custom[key]
    if key in conf_default:
        return conf_default[key]
    else:
        return default


def store_config(key, value):
    print(key, value)
    with open('config/config_custom.json', 'r+') as data_custom:
        conf_custom = json.loads(data_custom.read())
        conf_custom[key] = value
        data_custom.seek(0)
        data_custom.truncate()
        json.dump(conf_custom, data_custom, indent=4)
