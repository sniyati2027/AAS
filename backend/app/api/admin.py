from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User, UserStatus
from app.models.audit import AuditLog
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
):
    """Get all users."""
    result = await db.execute(select(User).order_by(desc(User.created_at)))
    users = result.scalars().all()
    return users


@router.get("/users/pending", response_model=list[UserResponse])
async def get_pending_users(
    db: AsyncSession = Depends(get_db),
):
    """Get all pending users awaiting approval."""
    result = await db.execute(
        select(User)
        .where(User.status == UserStatus.PENDING)
        .order_by(desc(User.created_at))
    )
    users = result.scalars().all()
    return users


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Approve a pending user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is already {user.status.value.lower()}",
        )

    user.status = UserStatus.APPROVED
    user.is_active = True
    user.approved_at = datetime.now(timezone.utc)

    await db.commit()
    return {"message": f"User {user.email} approved successfully"}


@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Reject a pending user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User is already {user.status.value.lower()}",
        )

    user.status = UserStatus.REJECTED
    user.is_active = False

    await db.commit()
    return {"message": f"User {user.email} rejected successfully"}


@router.get("/audit")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs."""
    result = await db.execute(
        select(AuditLog)
        .order_by(desc(AuditLog.timestamp))
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()

    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "ip_address": log.ip_address,
                "details": log.details,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/audit/export")
async def export_audit_logs(
    db: AsyncSession = Depends(get_db),
):
    """Export all audit logs as JSON."""
    result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.timestamp))
    )
    logs = result.scalars().all()

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "total_logs": len(logs),
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "ip_address": log.ip_address,
                "details": log.details,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
    }
