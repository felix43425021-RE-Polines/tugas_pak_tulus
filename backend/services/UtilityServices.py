from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Activity, Log, Blacklist, BlacklistReason, User

class UtilityService:
    """Service untuk menangani table_activity, table_log, dan table_blacklist"""

    # --- LOG AUDIT SYSTEM ---
    @staticmethod
    def create_activity_type(db: Session, description: str, deleted_by: int) -> Activity:
        """Membuat tipe aktivitas baru untuk log (e.g., 'LOGIN', 'CHECKOUT', 'LOGOUT')"""
        new_activity = Activity(
            description=description,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)
        return new_activity

    @staticmethod
    def record_log(db: Session, user_id: int, activity_id: int) -> Log:
        """Mencatat aktivitas yang dilakukan oleh user tertentu (Jembatan Lintas Skema)"""
        new_log = Log(
            user_id=user_id,
            activity_id=activity_id,
            created_at=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

    @staticmethod
    def get_user_logs(db: Session, user_id: int, limit: int = 50) -> List[Log]:
        """Melihat riwayat aktivitas log milik user tertentu"""
        statement = select(Log).where(Log.user_id == user_id).order_by(Log.created_at.desc()).limit(limit)
        return list(db.scalars(statement).all())

    # --- BLACKLIST MANAGEMENT ---
    @staticmethod
    def create_blacklist_reason(db: Session, cause_name: str, reason_text: str, deleted_by: int) -> BlacklistReason:
        """Membuat alasan pemblokiran baru (e.g., 'Spamming', 'Fraud/Penipuan')"""
        reason = BlacklistReason(
            cause_name=cause_name,
            reason=reason_text,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(reason)
        db.commit()
        db.refresh(reason)
        return reason

    @staticmethod
    def ban_user(db: Session, user_id: int, cause_id: int, deleted_by: int) -> Optional[Blacklist]:
        """Memasukkan user ke dalam daftar hitam (Blacklist)"""
        # Cek apakah user sudah masuk daftar hitam sebelumnya
        check_stmt = select(Blacklist).where(Blacklist.user_id == user_id)
        already_banned = db.scalars(check_stmt).first()

        if already_banned:
            return already_banned

        blacklist_entry = Blacklist(
            user_id=user_id,
            cause_id=cause_id,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(blacklist_entry)
        db.commit()
        db.refresh(blacklist_entry)
        return blacklist_entry

    @staticmethod
    def is_user_blacklisted(db: Session, user_id: int) -> bool:
        """Memvalidasi apakah user sedang dalam status diblokir (Untuk pengaman Login)"""
        statement = select(Blacklist).where(Blacklist.user_id == user_id, Blacklist.deleted_at == None)
        result = db.scalars(statement).first()
        return result is not None
