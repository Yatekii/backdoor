from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key = True, autoincrement = True)
	name = Column(String)
	level = Column(Integer)
	auth_token = Column(String)
	secret = Column(String)
	welcome_sound = Column(String)

	def __repr__(self):
		return '<User(id=\'%d\', name=\'%s\', level=\'%d\', auth_token=\'%s\' secret=\'%s\' welcome_sound=\'%s\'' % (self.id, self.name, self.level, self.auth_token, self.secret, self.welcome_sound)
