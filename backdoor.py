import queue
import signal

from connection_manager import ConnectionManager
import config
from query import Query
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
            self.handle_query(query)
        except queue.Empty:
            pass

    def issue_query(self, device, query):
        device = device if type(device) == str else device.pubkey
        if device in self.connection_manager.devices:
            self.connection_manager.devices[device].queries.put(query)
        else:
            print('Device with token %s is not registered.' % device)

    def open(self, device):
        query = Query()
        query.create_open(config.server_token)
        self.issue_query(device, query)

    def handle_query(self, query):
        if query.method == 'ACCESS':
            grant = Query()
            grant.create_grant(config.server_token, query.params[0])
            self.issue_query(query.token, grant)

bd = Backdoor()
bd.run()
