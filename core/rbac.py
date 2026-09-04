from enum import Enum
from typing import NamedTuple

from fastapi import Header

from app.config import settings
from app.core.errors import RBACPermissionDenied


class Role(str, Enum):
    OPERATOR = "OPERATOR"
    ENGINEER = "ENGINEER"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"


class UserContext(NamedTuple):
    user_id: str
    role: Role
    permissions: set[str]


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.OPERATOR: {
        "chat:execute",
        "document:read",
        "document:search",
        "process:analyze",
        "safety:analyze",
        "procedure:lookup",
        "comparison:execute",
    },
    Role.ENGINEER: {
        "chat:execute",
        "document:read",
        "document:search",
        "process:analyze",
        "safety:analyze",
        "procedure:lookup",
        "comparison:execute",
        "calculator:execute",
        "equipment:analyze",
        "report:generate",
        "image:analyze",
        "image:ingest",
    },
    Role.AUDITOR: {
        "audit:read",
        "audit:verify",
        "system:health",
    },
    Role.ADMIN: {
        "chat:execute",
        "document:read",
        "document:search",
        "document:ingest",
        "document:delete",
        "process:analyze",
        "safety:analyze",
        "procedure:lookup",
        "comparison:execute",
        "calculator:execute",
        "equipment:analyze",
        "report:generate",
        "image:analyze",
        "image:ingest",
        "audit:read",
        "audit:verify",
        "system:health",
        "system:admin",
    },
}

TOOL_ROLE_REQUIREMENTS: dict[str, set[Role]] = {
    "document_search": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "document_metadata": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "process_analysis": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "safety_analysis": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "procedure_lookup": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "document_comparison": {Role.OPERATOR, Role.ENGINEER, Role.ADMIN},
    "industrial_calculator": {Role.ENGINEER, Role.ADMIN},
    "equipment_analysis": {Role.ENGINEER, Role.ADMIN},
    "report_generation": {Role.ENGINEER, Role.ADMIN},
    "image_analysis": {Role.ENGINEER, Role.ADMIN},
}


def can_execute_tool(role: Role, tool_name: str) -> bool:
    """Check if the user's role is authorized to execute a specific industrial tool."""
    allowed = TOOL_ROLE_REQUIREMENTS.get(tool_name)
    if allowed is None:
        return role == Role.ADMIN
    return role in allowed


def get_current_user(
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
) -> UserContext:
    """
    Authenticate and extract sovereign user context from local trusted headers.
    In sovereign on-premise deployments, requests originate from authenticated enterprise
    gateway or authenticated local session.
    """
    raw_role = (x_user_role or settings.default_user_role).strip().upper()

    try:
        role = Role[raw_role]
    except KeyError:
        raise RBACPermissionDenied(
            f"Invalid user role '{x_user_role}'. Allowed roles: {[r.value for r in Role]}"
        )

    user_id = (x_user_id or f"sovereign_{role.value.lower()}_user").strip()
    permissions = ROLE_PERMISSIONS.get(role, set())

    return UserContext(user_id=user_id, role=role, permissions=permissions)


def require_permission(permission: str):
    """FastAPI dependency to enforce fine-grained sovereign permissions."""
    async def permission_checker(
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
        x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    ) -> UserContext:
        user = get_current_user(x_user_role=x_user_role, x_user_id=x_user_id)
        if permission not in user.permissions:
            raise RBACPermissionDenied(
                f"Role '{user.role.value}' lacks required permission '{permission}'."
            )
        return user

    return permission_checker


def require_role(allowed_roles: list[Role]):
    """FastAPI dependency to enforce role constraints."""
    async def role_checker(
        x_user_role: str | None = Header(default=None, alias="X-User-Role"),
        x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    ) -> UserContext:
        user = get_current_user(x_user_role=x_user_role, x_user_id=x_user_id)
        if user.role not in allowed_roles:
            role_names = [r.value for r in allowed_roles]
            raise RBACPermissionDenied(
                f"Role '{user.role.value}' is unauthorized. Permitted roles: {role_names}."
            )
        return user

    return role_checker

