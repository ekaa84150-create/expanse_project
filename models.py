from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Menunjuk ke properti 'user' di kelas Transaction
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    category = Column(String)
    price = Column(Integer)
    quantity = Column(Integer)
    date = Column(String)

    user_id = Column(String, ForeignKey("users.id"))

    # FIX FINAL: Variabel diganti jadi 'user' supaya klop dengan back_populates di kelas User!
    user = relationship("User", back_populates="transactions")