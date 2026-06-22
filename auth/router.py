from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from database import get_db
import models
from auth.schemas import UserCreateSchema, UserResponse, TokenResponse 
from auth.security import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# REGISTER USER
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreateSchema, db: Session = Depends(get_db)):
    # 1. Cek dulu apakah username sudah dipakai orang lain
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah terdaftar, Ton!"
        )
    
    # 2. Hash password biar aman
    hashed_pwd = hash_password(user_data.password)
    
    # 3. Buat objek user baru
    new_user = models.User(
        id=str(uuid.uuid4()),
        username=user_data.username,
        hashed_password=hashed_pwd
    )
    
    # 4. Simpan ke database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# LOGIN USER
@router.post("/login", response_model=TokenResponse)
def login_user(user_data: UserCreateSchema, db: Session = Depends(get_db)): 
    user = db.query(models.User).filter(models.User.username == user_data.username).first()

    # Jika user tidak ditemukan
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username Atau Password Salah"
        )
    
    # Cek password cocok gak
    is_password_correct = verify_password(user_data.password, user.hashed_password)

    # FIX FINAL: Typo ANOUTHORIZED sudah diganti ke UNAUTHORIZED
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau Password Salah"
        )
    
    # Kalo bener semua, buat token
    token_payload = {
        "user_id": user.id,
        "username": user.username
    }
    
    access_token = create_access_token(data=token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }