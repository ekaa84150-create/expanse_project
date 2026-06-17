from sqlalchemy import Column, String, Integer
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    amount = Column(Integer)
    category = Column(String)
    date = Column(String)