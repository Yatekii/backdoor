import queue
import signal

from connection_manager import ConnectionManager
import config
from query import Query


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
            job = self.connection_manager.queries.get(block=False)
            print('got query: ', job.query)
        except queue.Empty:
            pass

    def open(self, device):
        request = Query()
        request.create_open(config.server_token)
        self.connection_manager.devices[device.pubkey].queries(request)

bd = Backdoor()
bd.run()
