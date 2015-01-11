import functools

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


@handle_dbsession()
def list_user(session, **kwargs):
    users = session.query(models.User).filter_by().all()
    session.expunge_all()
    return users


@handle_dbsession()
def create_user(session, name, level, auth_token, secret, welcome_sound):
    user = models.User(name=name, level=level, auth_token=auth_token, secret=secret, welcome_sound=welcome_sound)
    session.add(user)
    session.commit()
    session.close()


@handle_dbsession()
def remove_user_by_name(session, name):
    session.delete(session.query(models.User).filter_by(name=name).first())
    session.commit()
    session.close()


@handle_dbsession()
def remove_user_by_token(session, *args, **kwargs):
    session.delete(session.query(models.User).filter_by(*args, **kwargs).first())
    session.commit()
    session.close()
