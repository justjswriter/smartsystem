from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_and_verify():
    password = "StrongPass123!"
    password_hash = hash_password(password)
    assert password_hash != password
    assert verify_password(password, password_hash)


def test_access_token_roundtrip():
    token = create_access_token("42", expires_minutes=10)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
