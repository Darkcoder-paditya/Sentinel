from __future__ import annotations
from datetime import datetime
from typing import Optional
from flask import current_app
from passlib.hash import bcrypt
import hashlib
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime
from .. import db


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def _hash_password(cls, password: str) -> str:
        # Hash password to avoid bcrypt 72-byte limit
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return bcrypt.hash(password_hash)

    @classmethod
    def create_admin(cls, email: str, password: str) -> "User":
        user = cls(email=email.lower(), password_hash=cls._hash_password(password), is_admin=True)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info("Admin user created: %s", email)
        return user

    @classmethod
    def register(cls, email: str, password: str, is_admin: bool = False) -> "User":
        user = cls(email=email.lower(), password_hash=cls._hash_password(password), is_admin=is_admin)
        db.session.add(user)
        db.session.commit()
        return user

    def verify_password(self, password: str) -> bool:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return bcrypt.verify(password_hash, self.password_hash)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() + "Z",
        }
