from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from database import get_db
from models import Operator, Tenant
from schemas import OperatorCreate
from security import verify_password, create_access_token, verify_token, get_password_hash

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_operator(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Operator:
    """Get current operator from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    operator_id: str = payload.get("sub")
    if operator_id is None:
        raise credentials_exception
        
    operator = db.query(Operator).filter(Operator.id == operator_id).first()
    if operator is None:
        raise credentials_exception
        
    if not operator.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive operator"
        )
        
    return operator

def authenticate_operator(db: Session, email: str, password: str) -> Optional[Operator]:
    """Authenticate operator with email and password."""
    operator = db.query(Operator).filter(Operator.email == email).first()
    if not operator:
        return None
    if not verify_password(password, operator.password_hash):
        return None
    return operator

def create_operator(db: Session, operator: OperatorCreate) -> Operator:
    """Create new operator. Aceita tenant_id ou tenant_name."""

    # Resolve tenant_id
    tenant_id = operator.tenant_id
    if not tenant_id and operator.tenant_name:
        tenant = db.query(Tenant).filter(Tenant.name == operator.tenant_name).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant não encontrado")
        tenant_id = tenant.id

    if not tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id ou tenant_name obrigatório")

    hashed_password = get_password_hash(operator.password)
    db_operator = Operator(
        tenant_id=tenant_id,
        name=operator.name,
        email=operator.email,
        password_hash=hashed_password,
        is_active=operator.is_active
    )
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

def update_operator_last_login(db: Session, operator: Operator) -> None:
    """Update operator's last login timestamp."""
    operator.last_login_at = datetime.utcnow()
    db.commit() 