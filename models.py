from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Table

Base = declarative_base()

token_device_table = Table('association', Base.metadata,
    Column('token_id', Integer, ForeignKey('tokens.id')),
    Column('device_id', Integer, ForeignKey('devices.id'))
)


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    value = Column(String)
    description = Column(String)
    flashed = Column(Boolean)
    expiry_date = Column(Date)
    owner_id = Column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    username = Column(String)
    password = Column(String)
    level = Column(Integer)
    name = Column(String)
    email = Column(String)
    nethzid = Column(String)
    welcome_sound = Column(String)
    tokens = relationship('Token', lazy='dynamic', backref='owner')


class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    description = Column(String)
    pubkey = Column(String)
    tokens = relationship('Token', secondary=token_device_table, backref='devices')