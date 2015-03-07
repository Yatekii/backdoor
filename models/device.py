from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Table


token_device_table = Table('association', Base.metadata,
    Column('token_id', Integer, ForeignKey('tokens.id')),
    Column('device_id', Integer, ForeignKey('devices.id'))
)


class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    description = Column(String)
    pubkey = Column(String)
    tokens = relationship('Token', secondary=token_device_table, backref='devices')
    used_by_default_by = relationship('User', backref='default_device')

