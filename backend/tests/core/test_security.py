import pytest

from app.core.security import hash_password, verify_password


def test_hash_password_does_not_return_plain_password() -> None:
    password = "correct horse battery staple"
    assert hash_password(password) != password


def test_hash_password_verifies_correct_password() -> None:
    password_hash = hash_password("correct password")
    assert verify_password("correct password", password_hash) is True


def test_verify_password_rejects_incorrect_password() -> None:
    password_hash = hash_password("correct password")
    assert verify_password("incorrect password", password_hash) is False


def test_hash_password_uses_random_salts() -> None:
    assert hash_password("same password") != hash_password("same password")


@pytest.mark.parametrize(
    "password_hash",
    [
        "not-a-supported-hash",
        "$argon2id$v=19$m=65536,t=3,p=4$malformed",
    ],
)
def test_verify_password_rejects_malformed_or_unsupported_hash(
    password_hash: str,
) -> None:
    assert verify_password("password", password_hash) is False
