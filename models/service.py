from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    fields = relationship('Field', lazy='dynamic', backref='owner', cascade='all, delete-orphan')
    data = relationship('ServiceData', lazy='dynamic', backref='service')