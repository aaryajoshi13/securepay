# Application-level role-based access control (RBAC).
# This is separate from the Cisco router ACL: the network ACL filters traffic,
# while this module decides which authenticated users can perform application actions.

ROLE_PERMISSIONS = {
    "HR": {"APP_STATUS"},
    "FINANCE": {"APP_STATUS", "FINANCE_REPORT"},
    "IT_ADMIN": {"APP_STATUS", "FINANCE_REPORT", "ADMIN_STATUS"},
    "SUPPORT": {"APP_STATUS"},
    "GUEST": {"APP_STATUS"},
}

def is_allowed(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, set())
