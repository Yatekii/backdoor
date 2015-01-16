import functools
import datetime
import json
import random
import string

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import orm

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


def str_to_date(string):
    data = string.split('-')
    return datetime.date(int(data[0]), int(data[1]), int(data[2]))


def generate_token():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(config.secret_length))


@handle_dbsession()
def list_users(session, **kwargs):
    users = session.query(models.User).filter_by(**kwargs).all()
    return users


@handle_dbsession()
def create_user(session, *args, **kwargs):
    user = models.User(*args, **kwargs)
    session.add(user)
    session.commit()
    session.close()


@handle_dbsession()
def remove_user_by_filter(session, *args, **kwargs):
    session.delete(session.query(models.User).filter_by(*args, **kwargs).first())
    session.commit()
    session.close()

@handle_dbsession()
def list_tokens(session, **kwargs):
    tokens = session.query(models.Token).filter_by(**kwargs).all()
    return tokens


@handle_dbsession()
def create_token(session, *args, **kwargs):
    token = models.Token(*args, **kwargs)
    if not orm.session.object_session(token):
        session.add(token)
    session.commit()
    session.close()


@handle_dbsession()
def remove_token_by_filter(session, *args, **kwargs):
    session.delete(session.query(models.Token).filter_by(*args, **kwargs).first())
    session.commit()
    session.close()

@handle_dbsession()
def revoke_token(session, id):
    token = session.query(models.Token).filter_by(id=id).first()
    if token:
        token.expiry_date = today() - datetime.timedelta(days=1)
        return True
    return False


@handle_dbsession()
def activate_token(session, id):
    token = session.query(models.Token).filter_by(id=id).first()
    if token:
        for date in config.semester_end:
            if date <= today():
                continue
            token.expiry_date = date
            return token.expiry_date
    return False

@handle_dbsession()
def users_to_json_by_filter(session, **kwargs):
    users = list_users(**kwargs)
    session.add_all(users)
    json_string = '{"users": ['
    for user in users:
        json_string += '{\n"name": "%s",\n "id": "%s"\n}, ' % (user.name, user.id)
    return json_string[:-2] + ']}'