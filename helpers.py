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


import functools
import datetime
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_


import config


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


import models


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
    json_string = '{"users": ['
    for user in users:
        json_string += '{\n"name": "%s",\n"username": "%s",\n "id": "%s"\n}, ' % (user.name, user.username, user.id)
    return json_string[:-2] + ']}'


@handle_dbsession()
def devices_to_json_by_filter(session, **kwargs):
    devices = session.query(models.Device).filter_by(**kwargs)
    json_string = '{"devices": ['
    for device in devices:
        json_string += '{\n"name": "%s",\n "id": "%s"\n}, ' % (device.name, device.id)
    return json_string[:-2] + ']}'