from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def create(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.user,
    ) -> User:
        u = User(name=name, email=email, password_hash=password_hash, role=role)
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u
