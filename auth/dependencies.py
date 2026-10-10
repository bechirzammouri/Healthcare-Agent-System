"""
FastAPI dependencies for authentication and role-based authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from auth import store
from auth.models import User
from auth.security import decode_access_token, hash_password, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pre-computed hash used to keep failed logins for unknown usernames roughly as
# slow as real ones, so response timing does not reveal which accounts exist.
_DUMMY_HASH = hash_password("not-a-real-password")

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Verify a username/password pair.

    Returns the user on success, None on bad credentials or a disabled account.
    """
    user = store.get_user(username)

    if user is None:
        # Burn comparable time so a missing user is not distinguishable by timing
        verify_password(password, _DUMMY_HASH)
        return None

    if not verify_password(password, user.password_hash):
        return None

    if user.disabled:
        return None

    return user.to_public()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Resolve the bearer token into the current user, or raise 401"""
    token_data = decode_access_token(token)
    if token_data is None:
        raise _CREDENTIALS_EXCEPTION

    user = store.get_user(token_data.username)
    if user is None or user.disabled:
        # Account removed or disabled after the token was issued
        raise _CREDENTIALS_EXCEPTION

    return user.to_public()


def require_role(*allowed_roles: str):
    """
    Build a dependency that allows only the given roles.

    Today every protected route uses require_role("doctor"); adding nurse,
    admin or patient later is just another argument here, with no change to
    the token format or the surrounding auth plumbing.
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role}' is not permitted to access "
                    "this resource"
                ),
            )
        return current_user

    return role_checker
