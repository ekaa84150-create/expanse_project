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
        try:
            datetime.strptime(value, "%d-%m-%Y")
            return value
        except ValueError:
            raise ValueError("Date must be in DD-MM-YYYY format")


# 2. CREATE TRANSACTION (POST /transactions)
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


# 3. READ ALL (GET /transactions)
@router.get("/")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).all()


# 4. SUMMARY BY CATEGORY (Statis ditaruh di atas dinamis)
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


# 5. TOTAL EXPENDITURE (Statis ditaruh di atas dinamis)
@router.get("/total")
def get_total_expenditure(db: Session = Depends(get_db)):
    all_transactions = db.query(models.Transaction).all()

    total_expenditure = 0
    total_item_bought = 0

    for t in all_transactions:
        total_expenditure += (t.price * t.quantity)
        total_item_bought += t.quantity
    return {
        "total_expenditure": total_expenditure,
        "total_item_bought": total_item_bought
    }

#5.5 Filter By Month And Year
@router.get ("/filter")
def filter_transactions_by_date(month: str, year: str, db: Session = Depends(get_db)):
    date_pattern = f"%-{month}-{year}"
    
    filtered_data = db.query(models.Transaction).filter(models.Transaction.date.like(date_pattern)).all()
    return {
        "month": month,
        "year": year,
        "total_found": len(filtered_data),
        "transactions": filtered_data
    }

# 6. READ BY ID (GET /transactions/{transaction_id})
@router.get("/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "message": "Transaction found",
        "transaction": transaction
    }


# 7. DELETE BY ID (DELETE /transactions/{transaction_id})
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


# 8. UPDATE BY ID (PUT /transactions/{transaction_id})
@router.put("/{transaction_id}")
def update_transaction(transaction_id: str, updated_transaction: TransactionSchema, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

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