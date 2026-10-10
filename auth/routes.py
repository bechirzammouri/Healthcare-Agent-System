"""
Authentication routes (OAuth2 password flow)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth.dependencies import authenticate_user, get_current_user
from auth.models import Token, User
from auth.security import create_access_token

router = APIRouter(tags=["authentication"])


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Exchange username/password for a JWT access token.

    This is the OAuth2 "password" grant: credentials are sent once here, and
    every subsequent request carries the returned token as a bearer credential
    instead of resending the password.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(username=user.username, role=user.role)
    return Token(access_token=token, token_type="bearer", expires_in=expires_in)


@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the identity behind the supplied bearer token"""
    return current_user
