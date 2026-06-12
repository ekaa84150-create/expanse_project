from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

# database sementara (RAM)
transactions = []

# schema
class Transaction(BaseModel):
    amount: int
    category: str
    date: str


# CREATE
@app.post("/transactions")
def create_transaction(transaction: Transaction):

    transaction_data = transaction.model_dump()
    transaction_data["id"] = str(uuid.uuid4())

    transactions.append(transaction_data)

    return {
        "message": "Transaction created successfully",
        "transaction": transaction_data
    }


# READ ALL
@app.get("/transactions")
def get_transactions():
    return transactions


# READ BY ID
@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str):

    for t in transactions:
        if t["id"] == transaction_id:
            return {
                "message": "Transaction found",
                "transaction": t
            }

    raise HTTPException(status_code=404, detail="transaction not found")


# DELETE
@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):

    for index, t in enumerate(transactions):
        if t["id"] == transaction_id:
            deleted_transaction = transactions.pop(index)

            return {
                "message": "Transaction deleted successfully",
                "deleted_transaction": deleted_transaction
            }

    raise HTTPException(status_code=404, detail="transaction not found")


# UPDATE
@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: str, transaction: Transaction):

    for index, t in enumerate(transactions):
        if t["id"] == transaction_id:

            updated_data = transaction.model_dump()
            updated_data["id"] = transaction_id

            transactions[index] = updated_data

            return {
                "message": "Transaction updated successfully",
                "updated_transaction": updated_data
            }

    raise HTTPException(status_code=404, detail="transaction not found")