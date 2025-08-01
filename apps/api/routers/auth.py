from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas import TokenWithOperator, OperatorCreate, Operator
from models import Operator as DBOperator
from auth import authenticate_operator, create_operator, update_operator_last_login
from security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(
    tags=["authentication"]
)

@router.post("/token", response_model=TokenWithOperator)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint to get JWT token."""
    operator = authenticate_operator(db, form_data.username, form_data.password)
    if not operator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(operator.id)},
        expires_delta=access_token_expires
    )
    
    update_operator_last_login(db, operator)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "operator": {
            "id": operator.id,
            "name": operator.name,
            "email": operator.email,
            "tenant_id": operator.tenant_id,
            "is_active": operator.is_active,
            "last_login_at": operator.last_login_at,
            "created_at": operator.created_at,
            "updated_at": operator.updated_at,
        }
    }

@router.post("/register", response_model=Operator)
async def register_operator(
    operator: OperatorCreate,
    db: Session = Depends(get_db)
):
    """Register new operator."""
    db_operator = db.query(DBOperator).filter(DBOperator.email == operator.email).first()
    if db_operator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_operator(db, operator) 