from sqlalchemy import Column, String, Integer
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    category = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)
    date = Column(String)