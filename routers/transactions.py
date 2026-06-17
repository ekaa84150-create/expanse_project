from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from database import get_db
import models

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

class TransactionSchema(BaseModel):
    amount: int = Field(gt=0, description="Amount must be greater than zero")
    category: str = Field(min_length=1, description="Category cannot be empty")
    date: str = Field(description="Date in YYYY-MM-DD format")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return value
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")


# 1. CREATE TRANSACTION (POST /transactions)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    db_transaction = models.Transaction(**transaction.model_dump())
    db_transaction.id = str(uuid.uuid4())

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return {
        "message": "Transaction created successfully",
        "transaction": db_transaction
    }


# 2. READ ALL (GET /transactions) -> INI YANG TADI HILANG!
@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()


# 3. READ BY ID (GET /transactions/{transaction_id})
@router.get("/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "message": "Transaction found",
        "transaction": transaction
    }


# 4. DELETE BY ID (DELETE /transactions/{transaction_id})
# Kita pakai status 200 OK (default) agar bisa mengirimkan response message ke React
@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }


# 5. UPDATE BY ID (PUT /transactions/{transaction_id})
@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, updated_transaction: TransactionSchema, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.amount = updated_transaction.amount
    transaction.category = updated_transaction.category
    transaction.date = updated_transaction.date

    db.commit()
    db.refresh(transaction)

    return {
        "message": "Transaction updated successfully",
        "transaction": transaction
    }