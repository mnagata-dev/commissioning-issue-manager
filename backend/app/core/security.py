"""Password hashing and verification utilities."""

from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError


_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password using the configured recommended algorithm."""
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether a password matches a supported stored hash."""
    try:
        return _password_hash.verify(password, password_hash)
    except PwdlibError:
        return False
