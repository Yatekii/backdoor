"""

    NFC controlled door access.
    Copyright (C) 2015  Yatekii yatekii(at)yatekii.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""


import json
import datetime
import logging


class Query:
    def __init__(self, token=None, method=None, service=None, params=None):
        self.logger = logging.getLogger('backdoor')
        self.query = {
            'auth': {
                'token': token,
                'time': None
            },
            'cmd': {
                'method': method,
                'service': service,
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

    def create_register_webui(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'REGISTER WEBUI'
        self.query['cmd']['params'] = [token]

    def create_unregister(self, auth_token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'UNREGISTER'

    def create_unknown_token(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'UNKNOWN'
        self.query['cmd']['params'] = [token]

    def create_deactivated_device(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'DEACTIVATED'
        self.query['cmd']['params'] = [token]

    def create_kick(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'KICK'
        self.query['cmd']['params'] = [token]

    def create_open(self, auth_token, device_token=None):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'OPEN'
        if device_token:
            self.query['cmd']['params'] = [device_token]

    def create_access(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'ACCESS'
        self.query['cmd']['params'] = [token]

    def create_grant(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'GRANT'
        self.query['cmd']['params'] = [token]

    def create_deny(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'DENY'
        self.query['cmd']['params'] = [token]

    def create_flash(self, auth_token, token, device_token=None):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'FLASH'
        self.query['cmd']['params'] = [token]
        if device_token:
            self.query['cmd']['params'] += [device_token]

    def create_flashed(self, auth_token, token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'FLASHED'
        self.query['cmd']['params'] = [token]

    def create_ping(self, auth_token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'PING'

    def create_pong(self, auth_token):
        self.query['auth']['token'] = auth_token
        self.query['cmd']['method'] = 'PONG'

    def create_valid_query_from_string(self, data):
        try:
            self.query = json.loads(data)
            return True
        except Exception as e:
            self.logger.debug('Query failed to parse.')
            self.logger.debug(e)
            return False

    def update_timestamp(self):
        self.query['auth']['time'] = str(datetime.datetime.utcnow().timestamp())

    def to_command(self):
        self.update_timestamp()
        return (json.dumps(self.query) + '\r\n').encode('utf-8')