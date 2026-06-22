from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

SECRET_KEY = "Its_Me_Koiis_Back_End"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#2 JWT TOKEN
def create_access_token(data: dict):
    to_encode = data.copy()
    #Atur waktu Kadaluarsa Token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #Masukin waktu exp ke dalam data token
    to_encode.update({"exp": expire})
    # Kunci dan Cetak Tokennya
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt