from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Optional
from uuid import uuid4

import jwt

from app.models import RefreshToken, User

JWT_SECRET = "linewatch-local-secret"


def hash_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


async def issue_tokens(user: User, device_id: str) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    access_token = jwt.encode({"sub": user.id, "exp": now + timedelta(minutes=15)}, JWT_SECRET, algorithm="HS256")
    refresh_token = jwt.encode(
        {"sub": user.id, "device_id": device_id, "exp": now + timedelta(days=14)},
        JWT_SECRET,
        algorithm="HS256",
    )
    expires_at = now + timedelta(days=14)
    saved = await RefreshToken.get_or_none(user=user, device_id=device_id)
    if saved:
        saved.token_hash = hash_token(refresh_token)
        saved.expires_at = expires_at
        await saved.save()
    else:
        await RefreshToken.create(
            id=str(uuid4()),
            user=user,
            device_id=device_id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
    return {"user_id": user.id, "access_token": access_token, "refresh_token": refresh_token}


async def refresh_tokens(user_id: str, device_id: str, refresh_token: str) -> Optional[dict[str, str]]:
    saved = await RefreshToken.get_or_none(user_id=user_id, device_id=device_id)
    if not saved or saved.expires_at <= datetime.now(timezone.utc) or saved.token_hash != hash_token(refresh_token):
        return None
    user = await User.get(id=user_id)
    return await issue_tokens(user, device_id)
