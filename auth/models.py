"""
Pydantic models for authentication
"""
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Roles a user account can hold (str subclass: compares equal to its value)"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"
    PATIENT = "patient"


# Role assigned to accounts created through the public /signup endpoint.
# Elevated roles are only granted out-of-band (scripts/create_user.py).
DEFAULT_SIGNUP_ROLE = Role.PATIENT


class Token(BaseModel):
    """OAuth2 token response returned by /token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Decoded JWT claims"""
    username: str
    role: str


class CreateUserRequest(BaseModel):
    """Request body for /signup (no role: clients cannot choose their privilege)"""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class User(BaseModel):
    """A user account (never carries the password hash)"""
    username: str
    role: str
    disabled: bool = False


class UserInDB(User):
    """Internal representation including the stored bcrypt hash"""
    password_hash: str

    def to_public(self) -> User:
        return User(username=self.username, role=self.role, disabled=self.disabled)
