from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    ActivityCreate,
    ActivityResponse,
    BlacklistCreate,
    BlacklistReasonCreate,
    BlacklistReasonResponse,
    BlacklistResponse,
    BlacklistStatusResponse,
    LogCreate,
    LogResponse,
)
from services.UserServices import UserService
from services.UtilityServices import UtilityService
from models import Activity, Blacklist, BlacklistReason, Log, User

router = APIRouter(prefix="/utility", tags=["Utility"])


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    return UtilityService.create_activity_type(
        db=db,
        description=payload.description,
        deleted_by=payload.deleted_by,
    )


@router.get("/activities", response_model=List[ActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    statement = (
        select(Activity)
        .where(Activity.deleted_at == None)
        .order_by(Activity.activity_id.desc())
    )
    return list(db.scalars(statement).all())


@router.post("/logs", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
def create_log(payload: LogCreate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db=db, user_id=payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    return UtilityService.record_log(
        db=db,
        user_id=payload.user_id,
        activity_id=payload.activity_id,
    )


@router.get("/logs")
def get_latest_logs(limit: int = 100, db: Session = Depends(get_db)):
    statement = (
        select(Log, User, Activity)
        .join(User, User.user_id == Log.user_id, isouter=True)
        .join(Activity, Activity.activity_id == Log.activity_id, isouter=True)
        .order_by(Log.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "log_id": log.log_id,
            "user_id": log.user_id,
            "username": user.username if user else None,
            "activity_id": log.activity_id,
            "activity_description": activity.description if activity else None,
            "created_at": log.created_at,
        }
        for log, user, activity in db.execute(statement).all()
    ]


@router.get("/users/{user_id}/logs", response_model=List[LogResponse])
def get_user_logs(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    return UtilityService.get_user_logs(db=db, user_id=user_id, limit=limit)


@router.get("/users/{user_id}/logs/detail")
def get_user_logs_detail(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    statement = (
        select(Log, Activity)
        .join(Activity, Activity.activity_id == Log.activity_id, isouter=True)
        .where(Log.user_id == user_id)
        .order_by(Log.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "log_id": log.log_id,
            "user_id": log.user_id,
            "activity_id": log.activity_id,
            "activity_description": activity.description if activity else None,
            "created_at": log.created_at,
        }
        for log, activity in db.execute(statement).all()
    ]


@router.post(
    "/blacklist-reasons",
    response_model=BlacklistReasonResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_blacklist_reason(payload: BlacklistReasonCreate, db: Session = Depends(get_db)):
    return UtilityService.create_blacklist_reason(
        db=db,
        cause_name=payload.cause_name,
        reason_text=payload.reason,
        deleted_by=payload.deleted_by,
    )


@router.get("/blacklist-reasons", response_model=List[BlacklistReasonResponse])
def get_blacklist_reasons(db: Session = Depends(get_db)):
    statement = (
        select(BlacklistReason)
        .where(BlacklistReason.deleted_at == None)
        .order_by(BlacklistReason.cause_id)
    )
    return list(db.scalars(statement).all())


@router.post("/blacklists", response_model=BlacklistResponse, status_code=status.HTTP_201_CREATED)
def ban_user(payload: BlacklistCreate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db=db, user_id=payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    return UtilityService.ban_user(
        db=db,
        user_id=payload.user_id,
        cause_id=payload.cause_id,
        deleted_by=payload.deleted_by,
    )


@router.get("/blacklists")
def get_blacklisted_users(db: Session = Depends(get_db)):
    statement = (
        select(Blacklist, User, BlacklistReason)
        .join(User, User.user_id == Blacklist.user_id)
        .join(BlacklistReason, BlacklistReason.cause_id == Blacklist.cause_id)
        .where(
            Blacklist.deleted_at == None,
            User.deleted_at == None,
            BlacklistReason.deleted_at == None,
        )
        .order_by(Blacklist.created_at.desc())
    )
    return [
        {
            "user_id": blacklist.user_id,
            "username": user.username,
            "cause_id": blacklist.cause_id,
            "reason": reason.reason,
            "created_at": blacklist.created_at,
        }
        for blacklist, user, reason in db.execute(statement).all()
    ]


@router.get("/blacklists/{user_id}/status", response_model=BlacklistStatusResponse)
def get_blacklist_status(user_id: int, db: Session = Depends(get_db)):
    return {
        "user_id": user_id,
        "is_blacklisted": UtilityService.is_user_blacklisted(db=db, user_id=user_id),
    }
