from . import Base
from sqlalchemy import Column, Integer, String


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    cancelled_count = Column(Integer, default=0)


