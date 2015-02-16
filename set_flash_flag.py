import socket
from query import Query
import config
import models
import helpers
import time
import sys


@helpers.handle_dbsession()
def flash_token(session, flashed):
    token = session.query(models.Token).filter_by(id=3).first()
    print(bool(flashed))
    token.flashed = bool(flashed)

flash_token(sys.argv[1] if len(sys.argv) > 1 else '')
