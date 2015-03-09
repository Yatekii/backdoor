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