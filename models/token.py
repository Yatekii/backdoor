from models.base import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(Date)
    name = Column(String)
    value = Column(String)
    description = Column(String)
    flashed = Column(Boolean)
    expiry_date = Column(Date)
    owner_id = Column(Integer, ForeignKey('users.id', ondelete='cascade'))