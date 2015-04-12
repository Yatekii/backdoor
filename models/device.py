from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Table
import helpers
import socket
import config
from query import Query


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
    is_online = Column(Boolean)
    is_enabled = Column(Boolean)

    @helpers.handle_dbsession()
    def revoke(sqlsession, device):
        error = False
        errors = []
        device = sqlsession.query(Device).filter_by(id=device).first()
        if device:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((config.api_host, config.api_port))
                temporary_token = helpers.generate_token()
                q = Query()
                q.create_register_webui(config.webui_token, temporary_token)
                s.send(q.to_command())
                q.create_kick(temporary_token, device.pubkey)
                s.send(q.to_command())
                q.create_unregister(temporary_token)
                s.send(q.to_command())
                s.close()
            except Exception:
                error = True
                errors.append(('flash', 'Connection to device failed.'))
        else:
                error = True
                errors.append(('device', 'Device does not exist.'))
        return error, errors
