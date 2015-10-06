from models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    uses_blueprint = Column(Boolean)