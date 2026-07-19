import json
import os


MANIFEST_FILE = os.path.join(
    os.path.dirname(__file__),
    "permissions.json"
)


def is_allowed(role, tool):

    with open(MANIFEST_FILE, "r") as f:
        permissions = json.load(f)

    if role not in permissions:
        return False

    return tool in permissions[role]["allowed_tools"]