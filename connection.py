import socket
import json
from threading import Thread
from queue import Queue
import queue

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
        print('Connected by', self.address)

    def run(self):
        while self.running:
            try:
                self.update()
                data = self.connection.recv(1024)
                self.data += data
                if len(data) == 0:
                    print('Connection lost; shutting down process.')
                    self.connection.close()
                    return

                data_stack = self.data.split(b'\r\n')
                self.data = data_stack.pop()
                for data in [x.decode('utf-8', errors='replace') for x in data_stack]:
                    self.update_queues(data)

            except socket.timeout as e:
                # this next if/else is a bit redundant, but illustrates how the
                # timeout exception is setup
                if e.args[0] == 'timed out':
                    continue
                else:
                    print(e)
                    self.running = False
            except socket.error as e:
                # Something else happened, handle error, exit, etc.
                print(e)
                self.running = False
            except Exception as e:
                if len(e.args[0]) == 0:
                    self.running = False
                else:
                    raise e
                    # got a message do something :)
        return

    def stop(self):
        self.connection.close()
        self.running = False

    def update(self):
        try:
            query = self.queries.get(block=False)
            self.connection.sendall(query.to_command())
        except queue.Empty:
            pass
        except Exception as e:
            print(e)

    @helpers.handle_dbsession()
    def update_queues(session, self, data):
        try:
            cmd = Query()
            if cmd.create_valid_query_from_string(data):
                try:
                    token = session.query(Device).filter_by(pubkey=cmd.token)
                    if cmd.method == 'REGISTER':
                        if token:
                            self.parent.devices[cmd.token] = self
                            print('registered new device with token %s' % cmd.token)
                        else:
                            print('unknown token %s tried to register and was rejected' % cmd.token)

                    elif cmd.method == 'REGISTER_WEBUI':
                        if cmd.token == config.webui_token:
                            self.parent.webuis[cmd.params[0]] = self
                            print('registered new webui with token %s' % cmd.params[0])
                        else:
                            print('unknown token %s tried to register as webui and was rejected' % cmd.token)

                    else:
                        self.parent.queries.put(cmd, block=False)
                except queue.Empty:
                    pass
                except Exception as e:
                    print(e)
            else:
                print('command discarded 1')
        except:
            print('command discarded 2')
            # discard command
            pass