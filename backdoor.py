import queue
import signal

from connection_manager import ConnectionManager
import config
from query import Query
from models import Token, Device
import helpers


class Backdoor:
    def stop(self, signal=None, frame=None):
        if signal:
            print('caught ctrl c; shutting down')
        self.connection_manager.stop()
        self.running = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.stop)
        self.running = True
        self.connection_manager = ConnectionManager(config.api_host, config.api_port)
        self.connection_manager.start()

    def run(self):
        while self.running:
            self.update()

    def update(self):
        try:
            query = self.connection_manager.queries.get(block=False)
            print('got query: ', query.query)
            if query.token in self.connection_manager.devices + self.connection_manager.webuis:
                self.handle_query(query)
            else:
                print('Request from non registered device. Discarded it.')
        except queue.Empty:
            pass

    def issue_query(self, device, query):
        device = device if type(device) == str else device.pubkey
        if device in self.connection_manager.devices:
            self.connection_manager.devices[device].queries.put(query)
        elif device in self.connection_manager.webuis:
            self.connection_manager.webuis[device].queries.put(query)
        else:
            print('Device or webui with token %s is not registered. Request was discarded.' % device)

    def open(self, device):
        query = Query()
        query.create_open(config.server_token)
        self.issue_query(device, query)

    @helpers.handle_dbsession()
    def handle_query(session, self, query):
        response = Query()
        if query.method == 'ACCESS':
            token = session.query(Token).filter_by(value=query.params[0]).first()
            device = session.query(Device).filter_by(pubkey_device=query.token).first()
            if token in device.tokens and token.expiry_date >= helpers.today():
                response.create_grant(config.server_token, query.params[0])

            else:
                response.create_deny(config.server_token, query.params[0])

            self.issue_query(query.token, response)

        elif query.method == 'FLASH':
            if query.token in self.connection_manager.webuis:
                if len(query.params) == 2:
                    response.create_flash(config.server_token, query.params[0])
                    self.issue_query(query.params[1], response)
                else:
                    print('Invalid flash request. Request has been discarded.')
            else:
                print('Request came from an unregistered webui. It is discarded.')

        elif query.method == 'FLASHED':
                session.query(Token).filter_by(query.params[0]).first().flashed = True
                print('Token has been flashed.')


bd = Backdoor()
bd.run()
