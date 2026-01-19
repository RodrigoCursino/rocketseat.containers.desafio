from src.infra.sqlalchemy.config.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float

class Products(Base):
    __tablename__ = "products"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100))
    price      = Column(Float(10,2))
    create_at  = Column(DateTime)
    update_at  = Column(DateTime)