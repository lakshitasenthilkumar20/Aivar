import jwt

SECRET_KEY = "my-secret-key"

roles = [
    ("support", "support_agent"),
    ("sales", "sales_agent"),
    ("admin", "admin")
]

for username, role in roles:
    token = jwt.encode(
        {
            "user": username,
            "role": role
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    print(f"{role}:")
    print(token)
    print()