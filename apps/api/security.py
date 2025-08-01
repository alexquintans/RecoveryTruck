from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Encryption Settings
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token."""
    try:
        print(f"🔍 Verificando token com SECRET_KEY: {SECRET_KEY[:20]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decodificado com sucesso: {payload}")
        return payload
    except JWTError as e:
        print(f"❌ Erro ao decodificar token: {str(e)}")
        return None

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return fernet.decrypt(encrypted_data.encode()).decode()

# Row Level Security (RLS) Policies
def get_tenant_policy(tenant_id: str) -> str:
    """Generate RLS policy for tenant isolation."""
    return f"tenant_id = '{tenant_id}'"

def get_operator_policy(operator_id: str, tenant_id: str) -> str:
    """Generate RLS policy for operator access."""
    return f"tenant_id = '{tenant_id}' AND (created_by = '{operator_id}' OR is_public = true)" 