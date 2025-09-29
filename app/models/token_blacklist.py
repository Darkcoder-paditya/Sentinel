from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Index
from .. import db


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)  # JWT ID
    user_id: Mapped[int] = mapped_column(db.Integer, nullable=False, index=True)
    revoked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Index for efficient lookups
    __table_args__ = (
        Index('idx_jti_user', 'jti', 'user_id'),
    )

    @classmethod
    def revoke_token(cls, jti: str, user_id: int, expires_at: datetime) -> "TokenBlacklist":
        """Add a token to the blacklist"""
        blacklisted_token = cls(
            jti=jti,
            user_id=user_id,
            expires_at=expires_at
        )
        db.session.add(blacklisted_token)
        db.session.commit()
        return blacklisted_token

    @classmethod
    def is_token_revoked(cls, jti: str) -> bool:
        """Check if a token is blacklisted"""
        return cls.query.filter_by(jti=jti).first() is not None

    @classmethod
    def cleanup_expired_tokens(cls) -> int:
        """Remove expired tokens from blacklist"""
        expired_count = cls.query.filter(cls.expires_at < datetime.utcnow()).count()
        cls.query.filter(cls.expires_at < datetime.utcnow()).delete()
        db.session.commit()
        return expired_count
