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

# 1. SCHEMA BARU (Memakai price & quantity, bukan amount lagi)
class TransactionSchema(BaseModel):
    category: str = Field(min_length=1, description="Category cannot be empty")
    price: int = Field(gt=0, description="Price must be greater than zero")
    quantity: int = Field(gt=0, description="Quantity must be at least 1")
    date: str = Field(description="Date in DD-MM-YYYY format")

    @field_validator('date')
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        # Kita sekalian samakan validasinya ke DD-MM-YYYY sesuai description di atas ya
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return value
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")


# 2. CREATE TRANSACTION (POST /transactions)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    # Karena schema input (Pydantic) dan model (SQLAlchemy) kolomnya sudah sama,
    # kita bisa langsung dump datanya otomatis ke database!
    db_transaction = models.Transaction(**transaction.model_dump())
    db_transaction.id = str(uuid.uuid4())

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return {
        "message": "Transaction created successfully",
        "transaction": db_transaction
    }


# 3. READ ALL (GET /transactions)
@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()


# 4. READ BY ID (GET /transactions/{transaction_id})
@router.get("/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "message": "Transaction found",
        "transaction": transaction
    }


# 5. DELETE BY ID (DELETE /transactions/{transaction_id})
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


# 6. UPDATE BY ID (PUT /transactions/{transaction_id})
@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, updated_transaction: TransactionSchema, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Di sini kita ganti pemetaan kolom lamanya menjadi price & quantity
    transaction.category = updated_transaction.category
    transaction.price = updated_transaction.price
    transaction.quantity = updated_transaction.quantity
    transaction.date = updated_transaction.date

    db.commit()
    db.refresh(transaction)

    return {
        "message": "Transaction updated successfully",
        "transaction": transaction
    }

#7 Summary By Category
@router.get("/summary/categories")
def get_category_summary(db: Session = Depends(get_db)):
    all_transactions = db.query(models.Transaction).all()
    summary = {}
    for t in all_transactions:
        total_cost = t.price * t.quantity
        if t.category in summary:
            summary[t.category] += total_cost
        else:
            summary[t.category] = total_cost
    return summary