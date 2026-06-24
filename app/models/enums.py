"""Domain enums for roles, permissions, and audit actions."""

from enum import Enum


class Role(str, Enum):
    """User roles for RBAC."""

    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"


class Permission(str, Enum):
    """Granular permissions mapped to roles."""

    CREATE_EMPLOYEE = "create_employee"
    UPDATE_EMPLOYEE = "update_employee"
    DELETE_EMPLOYEE = "delete_employee"
    MANAGE_USERS = "manage_users"
    VIEW_OWN_PROFILE = "view_own_profile"
    VIEW_EMPLOYEES = "view_employees"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.CREATE_EMPLOYEE,
        Permission.UPDATE_EMPLOYEE,
        Permission.DELETE_EMPLOYEE,
        Permission.MANAGE_USERS,
        Permission.VIEW_EMPLOYEES,
    },
    Role.MANAGER: {
        Permission.CREATE_EMPLOYEE,
        Permission.UPDATE_EMPLOYEE,
        Permission.VIEW_EMPLOYEES,
    },
    Role.EMPLOYEE: {
        Permission.VIEW_OWN_PROFILE,
    },
}


class AuditAction(str, Enum):
    """Audit log action types."""

    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE_EMPLOYEE = "CREATE_EMPLOYEE"
    UPDATE_EMPLOYEE = "UPDATE_EMPLOYEE"
    DELETE_EMPLOYEE = "DELETE_EMPLOYEE"
    ROLE_CHANGE = "ROLE_CHANGE"
    REGISTER = "REGISTER"
    GOOGLE_LOGIN = "GOOGLE_LOGIN"


class CollectionName(str, Enum):
    """MongoDB collection names."""

    USERS = "users"
    EMPLOYEES = "employees"
    AUDIT_LOGS = "audit_logs"
