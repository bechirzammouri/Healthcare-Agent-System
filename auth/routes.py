"""
Authentication routes (OAuth2 password flow)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import store
from auth.dependencies import authenticate_user, get_current_user
from auth.models import DEFAULT_SIGNUP_ROLE, CreateUserRequest, Token, User
from auth.security import create_access_token, hash_password
from auth.store import UserAlreadyExistsError

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


@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(payload: CreateUserRequest) -> User:
    """
    Create a new account with the default (lowest-privilege) role.

    The role is chosen by the server, never by the caller; elevated roles are
    granted out-of-band with scripts/create_user.py.
    """
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    try:
        return store.create_user(
            payload.username, password_hash, DEFAULT_SIGNUP_ROLE.value
        )
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )


@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Return the identity behind the supplied bearer token"""
    return current_user
