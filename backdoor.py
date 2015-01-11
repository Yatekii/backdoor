import functools

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from models import User


engine = create_engine(config.db, echo = config.sql_debug)
session_factory = sessionmaker(bind=engine)	

def handle_dbsession(session_factory):
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

@handle_dbsession(session_factory)
def list_user(session, **kwargs):
	users = session.query(User).filter_by().all()
	session.expunge_all()
	return users

def create_user(engine, name, level, auth_token, secret, welcome_sound):
	user = models.User(name=name, level=level, auth_token=auth_token, secret=secret, welcome_sound=welcome_sound)
	session_factory = sessionmaker(bind=engine)
	session = session_factory()
	session.add(user)
	session.commit()
	session.close()

def remove_user_by_name(engine, name):
	session_factory = sessionmaker(bind=engine)
	session = session_factory()
	session.delete(session.query(models.User).filter_by(name=name).first())
	session.commit()
	session.close()

def remove_user_by_token(engine, *args, **kwargs):
	session_factory = sessionmaker(bind=engine)
	session = session_factory()
	session.delete(session.query(models.User).filter_by(*args, **kwargs).first())
	session.commit()
	session.close()
