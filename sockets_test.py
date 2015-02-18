import json
import datetime
import socket
from query import Query
import config


# test = {"auth": {"token": "asdfghjkloiuztre", "time": "213241234123"}, "cmd": {"method": "REGISTER", "params": []}}
# test2 = {"auth": {"token": "asdfghjkloiuztre", "time": "213241234123"}, "cmd": {"method": "ACCESS", "params": ["asddasdasdasdasd"]}}
# print(json.dumps(test))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', config.api_port))
q = Query()
q.create_register('0123456789ABCDEFG')
print(q.to_command())
s.send(q.to_command())
q = Query()
q.create_unregister('0123456789ABCDEFG')
print(q.to_command())
s.sendall(q.to_command())

s.close()