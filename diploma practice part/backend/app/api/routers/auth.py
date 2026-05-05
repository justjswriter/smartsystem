from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserOut, TokenOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(data: UserCreate, db: Session = Depends(get_db)) -> TokenOut:
    return auth_service.register_user(db, data)


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenOut:
    return auth_service.login_user(db, data)


@router.get("/me", response_model=UserOut)
def me(
    current: User = Depends(get_current_user),
) -> UserOut:
    return UserOut.model_validate(current)
