"""Create demo user records with salted PBKDF2 password hashes.
Run: python3 make_users.py
Demo credentials are for coursework only; do not reuse real passwords.
"""
import hashlib
import json
import secrets
from pathlib import Path

USERS = {
    "hr_demo": ("HR", "HRdemo!234"),
    "finance_demo": ("FINANCE", "FinanceDemo!234"),
    "itadmin_demo": ("IT_ADMIN", "ITadminDemo!234"),
    "support_demo": ("SUPPORT", "SupportDemo!234"),
    "guest_demo": ("GUEST", "GuestDemo!234"),
}

def main():
    records = {}
    for username, (role, password) in USERS.items():
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000).hex()
        records[username] = {"role": role, "salt": salt.hex(), "password_hash": digest}
    path = Path(__file__).resolve().parent / "users.json"
    path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Created {path.name} with demo accounts.")
    print("Demo credentials:")
    for username, (role, password) in USERS.items():
        print(f"  {username} / {password}  (role={role})")

if __name__ == "__main__":
    main()
