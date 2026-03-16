import json
from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.user import User


class AuditService:
    """Service for logging audit events."""

    SENSITIVE_FIELDS = {"password", "hashed_password", "token", "secret", "api_key"}

    @staticmethod
    def mask_sensitive_data(data: Any) -> Any:
        """Recursively mask sensitive fields in data."""
        if isinstance(data, dict):
            return {
                key: "***MASKED***" if key.lower() in AuditService.SENSITIVE_FIELDS
                else AuditService.mask_sensitive_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [AuditService.mask_sensitive_data(item) for item in data]
        return data

    @staticmethod
    async def log_request(
        db: AsyncSession,
        user: Optional[User],
        method: str,
        path: str,
        status_code: int,
        ip_address: Optional[str] = None,
        request_body: Optional[dict] = None,
        response_body: Optional[dict] = None,
        duration_ms: Optional[float] = None,
    ):
        """Log an HTTP request."""
        details = {
            "method": method,
            "path": path,
            "status_code": status_code,
        }

        if request_body:
            details["request_body"] = AuditService.mask_sensitive_data(request_body)

        if response_body:
            details["response_body"] = AuditService.mask_sensitive_data(response_body)

        if duration_ms is not None:
            details["duration_ms"] = round(duration_ms, 2)

        audit_log = AuditLog(
            user_id=user.id if user else None,
            action=f"{method} {path}",
            ip_address=ip_address,
            details=json.dumps(details),
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit_log)
        await db.commit()

    @staticmethod
    async def log_user_action(
        db: AsyncSession,
        action: str,
        actor: User,
        ip_address: Optional[str] = None,
        target_user_id: Optional[int] = None,
        target_user_email: Optional[str] = None,
        **kwargs,
    ):
        """Log a custom user action."""
        details = {
            "actor_id": actor.id,
            "actor_email": actor.email,
            "actor_role": actor.role.value,
        }

        if target_user_id:
            details["target_user_id"] = target_user_id
        if target_user_email:
            details["target_user_email"] = target_user_email

        details.update(kwargs)

        audit_log = AuditLog(
            user_id=actor.id,
            action=action,
            ip_address=ip_address,
            details=json.dumps(details),
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit_log)
        await db.commit()


audit = AuditService()
