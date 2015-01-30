import socket
from threading import Thread
from queue import Queue

from connection import Connection


class ConnectionManager(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.running = True
        self.max_threads = 6
        self.connections = []
        self.devices = {}
        self.queries = Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        print('Server started! Listening on port %d' % port)

    def run(self):
        while self.running:
            self.socket.listen(self.max_threads)
            self.connections.append(Connection(self, self.socket.accept()))
            self.connections[-1].start()
            print('New connection')
        return

    def stop(self):
        for connection in self.connections:
            connection.stop()
        self.running = False