import jwt

SECRET_KEY = "my-secret-key"


def decode_token(token):
    """
    Decode JWT and return payload.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])