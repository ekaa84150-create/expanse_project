from fastapi import FastAPI
from routers import transactions # Import file router yang baru kita buat

app = FastAPI()

# Daftarkan router transaksi ke aplikasi utama FastAPI
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "Welcome to Expense Tracker API. Go to /docs for Swagger UI."}