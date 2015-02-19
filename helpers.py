import functools
import datetime
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import models


engine = create_engine(config.db, echo=config.sql_debug)
session_factory = sessionmaker(bind=engine)


def handle_dbsession():
    def handle_helper(f):
        @functools.wraps(f)
        def inner(*args, **kwargs):
            s = session_factory()
            try:
                r = f(s, *args, **kwargs)
                s.commit()
            finally:
                s.close()
            return r
        return inner
    return handle_helper


def today():
    return datetime.date.today()


def str_to_date(datestring):
    data = datestring.split('-')
    return datetime.date(int(data[0]), int(data[1]), int(data[2]))


def date_to_str(date):
    return date.strftime('%Y-%m-%d')


def generate_token():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(config.secret_length))


@handle_dbsession()
def users_to_json_by_filter(session, **kwargs):
    users = session.query(models.User).filter_by(**kwargs).all()
    session.add_all(users)
    json_string = '{"users": ['
    for user in users:
        json_string += '{\n"name": "%s",\n "id": "%s"\n}, ' % (user.name, user.id)
    return json_string[:-2] + ']}'


@handle_dbsession()
def devices_to_json_by_filter(session, **kwargs):
    devices = session.query(models.Device).filter_by(**kwargs)
    json_string = '{"devices": ['
    for device in devices:
        json_string += '{\n"name": "%s",\n "id": "%s"\n}, ' % (device.name, device.id)
    return json_string[:-2] + ']}'