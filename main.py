from fastapi import FastAPI
from routers import transactions # Import file router transaksi
from auth import router as auth_router # 1. IMPORT ROUTER AUTH YANG BARU LU BIKIN!

from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Daftarkan router transaksi ke aplikasi utama FastAPI
app.include_router(transactions.router)

# 2. DAFTARKAN ROUTER AUTENTIKASI BARU LU DI SINI!
app.include_router(auth_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to Expense Tracker API. Go to /docs for Swagger UI."} #