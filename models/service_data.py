from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class ServiceData(Base):
    __tablename__ = 'service_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String)
    value = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='cascade', use_alter=True, name='user_id'))
    device_id = Column(Integer, ForeignKey('devices.id', ondelete='cascade'))
    service_id = Column(Integer, ForeignKey('services.id', ondelete='cascade'))