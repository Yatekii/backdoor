from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    creation_date = Column(Date)
    expiry_date = Column(Date)
    owner_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    level = Column(Integer)
    welcome_sound = Column(String)
    tokens = relationship('Token', lazy='dynamic', backref='owner')
