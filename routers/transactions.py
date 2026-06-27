from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from datetime import datetime
from auth.security import get_current_user # Satpam token JWT
import uuid
import database
from database import get_db
import models

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


#         1. VALIDASI SCHEMA DATA

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



#         2. CRUD & LOGIC ENDPOINTS


# 🟢 CREATE TRANSACTION (Otomatis ngiket user_id dari token)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionSchema, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    db_transaction = models.Transaction(**transaction.model_dump())
    db_transaction.id = str(uuid.uuid4())
    db_transaction.user_id = current_user.id # Ambil id dari akun yg login!

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return {
        "message": "Transaction created successfully",
        "transaction": db_transaction
    }


# 🔵 READ ALL (Cuma nampilin transaksi milik user yang lagi login)
@router.get("/")
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    return db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()


# 📊 SUMMARY BY CATEGORY (Cuma ngitung pengeluaran milik user yang lagi login)
@router.get("/summary/categories")
def get_category_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()
    summary = {}
    for t in user_transactions:
        total_cost = t.price * t.quantity
        if t.category in summary:
            summary[t.category] += total_cost
        else:
            summary[t.category] = total_cost
    return summary


# 💰 TOTAL EXPENDITURE (Cuma kalkulasi total belanjaan user yang lagi login)
@router.get("/total")
def get_total_expenditure(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    user_transactions = db.query(models.Transaction).filter(models.Transaction.user_id == current_user.id).all()

    total_expenditure = 0
    total_item_bought = 0

    for t in user_transactions:
        total_expenditure += (t.price * t.quantity)
        total_item_bought += t.quantity
        
    return {
        "total_expenditure": total_expenditure,
        "total_item_bought": total_item_bought
    }


# 📅 FILTER BY MONTH AND YEAR (Cuma nyari transaksi user yang lagi login)
@router.get("/filter")
def filter_transactions_by_date(
    month: str, 
    year: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    # Pola pencarian kecocokan string tanggal
    date_pattern = f"%{month}-{year}"
    
    filtered_data = db.query(models.Transaction).filter(
        models.Transaction.user_id == current_user.id,
        models.Transaction.date.like(date_pattern)
    ).all()
    
    return {
        "month": month,
        "year": year,
        "total_found": len(filtered_data),
        "transactions": filtered_data
    }


# 🔍 READ BY ID (Cek ID spesifik dan pastiin itu emang milik dia)
@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")

    return {
        "message": "Transaction found",
        "transaction": transaction
    }


# ❌ DELETE BY ID
@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }


# 🔄 UPDATE BY ID
@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: str, 
    updated_transaction: TransactionSchema, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Wajib Login
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")

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