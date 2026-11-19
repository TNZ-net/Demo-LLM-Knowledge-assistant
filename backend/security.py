import os, datetime as dt
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


_hasher = PasswordHash.recommended()      

def hash_password(password: str) -> str:
    return _hasher.hash(password)         

def verify_password(password: str, hashed: str) -> bool:
    return _hasher.verify(password, hashed)

load_dotenv()
SECRET = os.environ["JWT_SECRET"]
ALGO = "HS256"

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),                                  
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1), 
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str) -> int:
    payload = jwt.decode(token, SECRET, algorithms=[ALGO])    
    return int(payload["sub"])