from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from routers import transactions 
from auth import router as auth_router # Mengarah ke auth/__init__.py atau auth/router.py

from database import engine
import models



models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Mengaktifkan CORS agar Frontend aman dari blokir browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wajib dipasang buat session tracking Google OAuth
app.add_middleware(SessionMiddleware, secret_key="Its_Me_Koiis_Back_End")

app.include_router(transactions.router)
app.include_router(auth_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to Expense Tracker API. Go to /docs for Swagger UI."}