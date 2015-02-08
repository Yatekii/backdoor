import socket
from threading import Thread
from queue import Queue
import logging

from connection import Connection


class ConnectionManager(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.running = True
        self.max_threads = 6
        self.connections = []
        self.devices = {}
        self.webuis = {}
        self.queries = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.settimeout(2.0)
        self.logger = logging.getLogger('backdoor')
        self.logger.info('Server started! Listening on port %d' % port)

    def run(self):
        while self.running:
            try:
                self.socket.listen(self.max_threads)
                self.connections.append(Connection(self, self.socket.accept()))
                self.logger.info('New connection.')
                self.connections[-1].start()
            except socket.timeout as e:
                if e.args[0] == 'timed out':
                    continue
                else:
                    self.logger.exception('Caught exception in connection manager run():')
                    self.logger.exception(e)

            except socket.error as e:
                self.logger.exception('Caught exception in connection manager run():')
                self.logger.exception(e)

            except Exception as e:
                if len(e.args[0]) == 0:
                    self.logger.exception('Caught exception in connection manager run():')
                    self.logger.exception(e)

        self.logger.info('Connection manager was shut down.')
        return

    def stop(self):
        self.logger.info('Halt all threads.')
        for connection in self.connections:
            connection.stop()
        self.logger.info('Halted all threads.')
        self.running = False