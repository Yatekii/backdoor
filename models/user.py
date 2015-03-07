from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship


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
    default_device_id = Column(Integer, ForeignKey('devices.id'))
    tokens = relationship('Token', lazy='dynamic', backref='owner', cascade='all, delete-orphan')