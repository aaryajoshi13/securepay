import hashlib
import hmac
import json
from pathlib import Path

USERS_FILE = Path(__file__).resolve().parent / "users.json"

def _password_hash(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000).hex()

def authenticate(username: str, password: str):
    try:
        users = json.loads(USERS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    record = users.get(username)
    if not record:
        # Do a dummy hash to reduce obvious timing differences for unknown users.
        _password_hash(password, "00112233445566778899aabbccddeeff")
        return None

    candidate = _password_hash(password, record["salt"])
    if hmac.compare_digest(candidate, record["password_hash"]):
        return {"username": username, "role": record["role"]}
    return None
