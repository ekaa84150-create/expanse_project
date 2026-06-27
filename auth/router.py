from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
import os
import uuid

from database import get_db
import models
from auth.schemas import UserCreateSchema, UserResponse, TokenResponse 
import auth.security as security

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# KONFIGURASI GOOGLE OAUTH
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
print("CLIENT SECRET:", os.getenv("GOOGLE_CLIENT_SECRET"))

# 1. ROUTE LOGIN GOOGLE
@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

# 2. ROUTE CALLBACK GOOGLE
@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Gagal Mengambil Data Dari Google") 

        email = user_info.get("email")
        username = user_info.get("name")

        user = db.query(models.User).filter(models.User.username == email).first()

        if not user:
            user = models.User(
                id=str(uuid.uuid4()),
                username=email,
                hashed_password=security.hash_password(str(uuid.uuid4()))
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        token_payload = {"user_id": user.id, "username": user.username}
        access_token = security.create_access_token(data=token_payload)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": f"Hallo {username}, Kamu berhasil login menggunakan google"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Login Gagal: {str(e)}")

# 3. REGISTER MANUAL
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah terdaftar")
    
    new_user = models.User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        hashed_password=security.hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 4. LOGIN MANUAL
@router.post("/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau Password Salah"
        )

    if not security.verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau Password Salah"
        )

    token_payload = {
        "user_id": user.id,
        "username": user.username
    }

    access_token = security.create_access_token(token_payload)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }