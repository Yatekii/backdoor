from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class FieldChoice(Base):
    __tablename__ = 'field_choices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    description = Column(String)
    field_id = Column(Integer, ForeignKey('fields.id', ondelete='cascade'))