from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate, UserLogin, TokenOut


def register_user(db: Session, data: UserCreate) -> TokenOut:
    repo = UserRepository(db)
    if repo.get_by_email(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = repo.create(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=UserRole.user,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    return _make_token_out(user)


def login_user(db: Session, data: UserLogin) -> TokenOut:
    repo = UserRepository(db)
    user = repo.get_by_email(data.email)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return _make_token_out(user)


def _make_token_out(user: User) -> TokenOut:
    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token, token_type="bearer")
