import json
import datetime


class Query:
    def __init__(self, token=None, method=None, params=None):
        self.query = {
            'auth': {
                'token': token,
                'time': None
            },
            'cmd': {
                'method': method,
                'params': params
            }
        }

    @property
    def token(self):
        return self.query['auth']['token']

    @token.setter
    def token(self, value):
        self.query['auth']['token'] = value

    @property
    def time(self):
        return self.query['auth']['time']

    @time.setter
    def time(self, value):
        self.query['auth']['time'] = value

    @property
    def method(self):
        return self.query['cmd']['method']

    @method.setter
    def method(self, value):
        self.query['cmd']['method'] = value

    @property
    def params(self):
        return self.query['cmd']['params']

    @params.setter
    def params(self, value):
        self.query['cmd']['params'] = value

    def create_register(self, auth_token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'REGISTER'

    def create_open(self, auth_token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'OPEN'

    def create_access(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'ACCESS'
        self.query['cmd']['params'] = [token]

    def create_grant(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'GRANT'
        self.query['cmd']['params'] = [token]

    def create_valid_query_from_string(self, data):
        print(data)
        try:
            self.query = json.loads(data)
            return True
        except Exception as e:
            print(e)
            print('Query failed to parse')
            return False

    def update_timestamp(self):
        self.query['auth']['time'] = str(datetime.datetime.utcnow().timestamp())

    def to_command(self):
        self.update_timestamp()
        return (json.dumps(self.query) + '\n').encode('utf-8')