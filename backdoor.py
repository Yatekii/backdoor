import queue
import signal
import logging

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

    def open(self, device):
        query = Query()
        query.create_open(config.server_token)
        self.issue_query(device, query)

    @helpers.handle_dbsession()
    def handle_query(session, self, query):
        response = Query()
        self.logger.debug('Handle query:')
        self.logger.debug(query.query)
        if query.method == 'ACCESS':
            token = session.query(Token).filter_by(value=query.params[0]).first()
            device = session.query(Device).filter_by(pubkey_device=query.token).first()
            if len(query.params) == 1:
                if token in device.tokens and token.expiry_date >= helpers.today():
                    response.create_grant(config.server_token, query.params[0])
                    self.logger.info('Granted access to token %s at device %s' % (query.params[0], query.token))
                else:
                    response.create_deny(config.server_token, query.params[0])
                    self.logger.info('Denied access to token %s at device %s' % (query.params[0], query.token))

                self.issue_query(query.token, response)
            else:
                self.logger.debug('Broken query. Expected exactly 1 parameter.')

        elif query.method == 'FLASH':
            self.logger.info('Requested flash of token %s at device %s' % (query.params[0], query.params[1]))
            if len(query.params) == 2:
                if query.token in self.connection_manager.webuis:
                    response.create_flash(config.server_token, query.params[0])
                    self.issue_query(query.params[1], response)
                else:
                    self.logger.info('Requested flash came from a non webui or an unregistered one. It was discarded.')
            else:
                self.logger.debug('Broken query. Expected exactly 2 parameters.')

        elif query.method == 'FLASHED':
            if len(query.params) == 1:
                session.query(Token).filter_by(value=query.params[0]).first().flashed = True
                self.logger.debug('Token %s was flashed' % query.params[0])
            self.logger.debug('Broken query. Expected exactly 1 parameter.')

bd = Backdoor()
bd.run()
