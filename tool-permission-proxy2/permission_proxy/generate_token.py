import jwt

SECRET_KEY = "my-secret-key"

payload = {
    "user": "lakshita",
    "role": "support_agent"
}

token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print(token)