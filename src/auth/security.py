import bcrypt
import hashlib
from src.config import settings

def _get_peppered_password(password: str) -> bytes:
    peppered = password + settings.PASSWORD_PEPPER

    sha256_hash = hashlib.sha256(peppered.encode()).hexdigest()
    
    return sha256_hash.encode()

def get_password_hash(password: str) -> str:

    prepared_password = _get_peppered_password(password)

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(prepared_password, salt)
    
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        prepared_password = _get_peppered_password(plain_password)
        return bcrypt.checkpw(prepared_password, hashed_password.encode('utf-8'))
    except Exception:
        return False