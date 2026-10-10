"""
Authentication and authorization package.

Implements the OAuth2 password flow with self-issued JWTs. Credentials are
stored in a local SQLite database (see auth/store.py) deliberately kept
outside Neo4j, so the agent's read-only Cypher surface cannot reach them.
"""
from auth.models import Token, TokenData, User
from auth.dependencies import get_current_user, require_role

__all__ = ["Token", "TokenData", "User", "get_current_user", "require_role"]
