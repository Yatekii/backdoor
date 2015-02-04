import json
import datetime
import socket
from query import Query
import config
import models
import helpers
import time


@helpers.handle_dbsession()
def simulate_reader(session):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', config.api_port))
    q = Query()
    device = session.query(models.Device).filter_by(id=config.flash_device).first()
    q.create_register(device.pubkey)
    print(q.to_command())
    s.send(q.to_command())
    cmd = Query()
    cmd.create_valid_query_from_string(s.recv(1024).split(b'\r\n')[0].decode('utf-8'))
    q.create_flashed(device.pubkey, cmd.params[0])
    print(q.to_command())
    s.send(q.to_command())
    time.sleep(10)
    s.close()

simulate_reader()