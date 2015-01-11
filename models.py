from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    expiry_date = Column(Date)
    owner = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    level = Column(Integer)
    welcome_sound = Column(String)
    tokens = relationship('Token', backref='users')

    def __repr__(self):
        return '<User(id=\'%s\', name=\'%s\', level=\'%s\', auth_token=\'%s\' secret=\'%s\' welcome_sound=\'%s\'>' % (self.id, self.name, self.level, self.auth_token, self.secret, self.welcome_sound)
