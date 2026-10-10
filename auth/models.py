"""
Pydantic models for authentication
"""
from pydantic import BaseModel


class Token(BaseModel):
    """OAuth2 token response returned by /token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Decoded JWT claims"""
    username: str
    role: str


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
