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
