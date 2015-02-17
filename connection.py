import socket
import logging
from threading import Thread
from queue import Queue
import queue
import time

from models import Token, Device
from query import Query
import helpers
import config


class Connection(Thread):
    def __init__(self, parent, incomming_connection):
        Thread.__init__(self)
        self.running = True
        self.parent = parent
        self.data = b''
        self.connection, self.address = incomming_connection
        self.connection.settimeout(2.0)
        self.queries = Queue()
        self.other = None
        self.type = None
        self.logger = logging.getLogger('backdoor')
        self.logger.info('Connected with %s, %d' % (self.address[0], self.address[1]))
        self.last_ping = time.time()
        self.pinged = False

    def shutdown(self):
        self.logger.info('Shutting down connection thread.')
        self.running = False
        if self.other in self.parent.webuis:
            del self.parent.webuis[self.other]
        elif self.other in self.parent.devices:
            del self.parent.devices[self.other]
        try:
            self.connection.close()
        except OSError as e:
            if e.args[0] == 9:
                pass
            else:
                raise e
        self.logger.info('Successfully shut down connection thread.')

    def run(self):
        while self.running:
            if time.time() - self.last_ping > config.ping_interval + config.pong_interval:
                self.logger.info('Got no PING from %s in time. Closing connection' % self.other)
                return self.shutdown()

            elif time.time() - self.last_ping > config.ping_interval and not self.pinged:
                query = Query()
                query.create_ping(config.server_token)
                self.connection.sendall(query.to_command())
                self.pinged = True
                self.logger.info('Sent PING to %s.' % self.other)

            try:
                self.update()
                data = self.connection.recv(1024)
                self.data += data

                if len(data) == 0:
                    return self.shutdown()

                data_stack = self.data.split(b'\r\n')
                self.data = data_stack.pop()
                for data in [x.decode('utf-8', errors='replace') for x in data_stack]:
                    self.update_queues(data)

            except socket.timeout as e:
                if e.args[0] == 'timed out':
                    continue
                else:
                    self.logger.exception('Shutting down connection thread (%s, %d) due to caught exception:' % (self.address[0], self.address[1]))
                    self.logger.exception(e)
                    return self.shutdown()

            except OSError as e:
                if e.args[0] == 9:
                    self.logger.info('Connection lost.')
                    return self.shutdown()
                else:
                    raise e

            except socket.error as e:
                self.logger.exception('Shutting down connection thread (%s, %d) due to caught exception:' % (self.address[0], self.address[1]))
                self.logger.exception(e)
                return self.shutdown()

            except Exception as e:
                if len(e.args[0]) == 0:
                    self.logger.exception('3Shutting down connection thread (%s, %d) due to caught exception:' % (self.address[0], self.address[1]))
                    self.logger.exception(e)
                    return self.shutdown()
        return

    def stop(self):
        self.logger.info('Regular shutdown of connection thread (%s, %d).' % (self.address[0], self.address[1]))
        self.shutdown()

    def update(self):
        try:
            query = self.queries.get(block=False)
            self.connection.sendall(query.to_command())
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.exception('Caught exception in thread (%s, %d) whilst trying to send query:' % (self.address[0], self.address[1]))
            self.logger.exception(query.query)
            self.logger.exception(e)

    @helpers.handle_dbsession()
    def update_queues(session, self, data):
        try:
            cmd = Query()
            if cmd.create_valid_query_from_string(data):
                try:
                    device = session.query(Device).filter_by(pubkey=cmd.token)
                    if cmd.method == 'REGISTER':
                        if device:
                            self.parent.devices[cmd.token] = self
                            self.other = cmd.token
                            self.type = 'device'
                            self.logger.info('Registered new device with token %s.' % cmd.token)
                        else:
                            self.logger.info('Unknown token %s tried to register and was rejected.' % cmd.token)

                    elif cmd.method == 'REGISTER WEBUI':
                        if cmd.token == config.webui_token:
                            self.parent.webuis[cmd.params[0]] = self
                            self.other = cmd.token
                            self.type = 'webui'
                            self.logger.info('Registered new webui with token %s.' % cmd.params[0])
                        else:
                            self.logger.info('Unknown token %s tried to register as webui and was rejected.' % cmd.token)

                    elif cmd.method == 'UNREGISTER':
                        if cmd.token == self.other:
                            self.logger.info('%s just unregistered. Shutting down.' % self.other)
                            return self.shutdown()

                    elif cmd.method == 'PONG':
                        if self.pinged and config.ping_interval + config.pong_interval > self.last_ping - time.time():
                            self.last_ping = time.time()
                            self.pinged = False
                            self.logger.info('Got PONG from %s.' % cmd.token)

                    else:
                        self.parent.queries.put(cmd, block=False)
                except queue.Empty:
                    pass
                except Exception as e:
                    self.logger.exception('Caught exception whilst processing command:')
                    self.logger.exception(cmd.query)
                    self.logger.exception(e)
            else:
                self.logger.info('Discarded command:')
                self.logger.info(data)
        except:
            self.logger.info('Discarded command:')
            self.logger.info(data)