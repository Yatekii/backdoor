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
        return json.dumps(self.query) + '\n'