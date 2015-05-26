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


import queue
import signal
import logging
import importlib

import models
import services

from connection_manager import ConnectionManager
import config
from query import Query
from models import Token, Device
import helpers


class Backdoor:
    def stop(self, signal=None, frame=None):
        if signal:
            self.logger.info('Caught SIGINT.')
        self.logger.info('Shutting down.')
        self.connection_manager.stop()
        self.running = False

    def __init__(self):
        self.logger = logging.getLogger('backdoor')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.info('Starting backdoor.')
        signal.signal(signal.SIGINT, self.stop)
        self.running = True
        self.connection_manager = ConnectionManager(config.api_host, config.api_port)
        self.connection_manager.start()
        self.methods = {}
        self.services = []
        self.load_services()

    def run(self):
        while self.running:
            self.update()
        self.logger.info('Backdoor was shut down.')

    def update(self):
        try:
            query = self.connection_manager.queries.get(block=False)
            self.logger.debug('Got query:')
            self.logger.debug(query.query)
            if query.token in self.connection_manager.devices or query.token in self.connection_manager.webuis:
                self.handle_query(query)
            else:
                self.logger.info('A request from anon registered device was discarded:')
                self.logger.info(query.query)
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.exception('Caught exception during the update process:')
            self.logger.exception(e)

    def issue_query(self, device, query):
        device = device if type(device) == str else device.pubkey
        if device in self.connection_manager.devices:
            self.connection_manager.devices[device].queries.put(query)
        elif device in self.connection_manager.webuis:
            self.connection_manager.webuis[device].queries.put(query)
        else:
            self.logger.info('Device or webui with token %s is not registered. Request was discarded:' % device)
            self.logger.info(query.query)

    def add_method(self, service, name, fn):
        self.methods['%s_%s' % (service, name)] = fn[0]
        self.logger.info('Loaded method %s: %s' % ('%s_%s' % (service, name), fn[1]))

    @helpers.handle_dbsession()
    def load_services(sqlsession, self):
        s = sqlsession.query(models.Service).filter_by().all()
        i = 0
        for service in s:
            self.logger.info('Loading service %s' % service.name)
            self.load_service(service.name)
            self.services.append(service.name)
            i += 1
            self.logger.info('Finished loading service %s' % service.name)

        self.logger.info('Loaded %d modules' % i if i != 1 else 'Loaded 1 module')

    def load_service(self, service):
        if service not in self.services:
            try:
                m = importlib.import_module('.%s' % service, 'services')
                for ability in m.__methods__:
                    self.add_method(service, ability, m.__methods__[ability])
            except Exception as e:
                self.logger.info('Failed to load service %s due to a faulty module' % service)
                self.logger.info(e)
                self.stop()
                return False
        else:
            self.logger.info('Tried to load a yet registered service %s. Skipping' % service)
            return False
        return True

    def handle_query(self, query):
        self.logger.debug('Handle query:')
        if ('%s_%s' % (query.query['cmd']['service'], query.method)) in self.methods:
            self.methods['%s_%s' % (query.query['cmd']['service'], query.method)](self, query)
        else:
            self.logger.debug('Broken query. Unknown method: %s.' % query.method)

bd = Backdoor()
bd.run()
