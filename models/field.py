from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Type:
    text = 0
    int = 1
    bool = 2

class Field(Base):
    __tablename__ = 'fields'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('services.id', ondelete='cascade'))
    key = Column(String)
    choices = relationship('FieldChoice', lazy='dynamic', backref='field', cascade='all, delete-orphan')
    description = Column(String)
    condition = Column(String)
    type = Column(Integer)