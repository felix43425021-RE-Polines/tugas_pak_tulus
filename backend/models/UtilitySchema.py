from datetime import datetime
from typing import List, Optional, Text
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base


class Activity(Base):
    __tablename__ = "table_activity"
    __table_args__ = {"schema": "schema_utility"}

    activity_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    logs: Mapped[List["Log"]] = relationship(back_populates="activity")


class Log(Base):
    __tablename__ = "table_log"
    __table_args__ = {"schema": "schema_utility"}

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_user.user_id"), primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("schema_utility.table_activity.activity_id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="logs")
    activity: Mapped["Activity"] = relationship(back_populates="logs")


class BlacklistReason(Base):
    __tablename__ = "table_blacklist_reason"
    __table_args__ = {"schema": "schema_utility"}

    cause_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cause_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    blacklists: Mapped[List["Blacklist"]] = relationship(back_populates="reason")


class Blacklist(Base):
    __tablename__ = "table_blacklist"
    __table_args__ = {"schema": "schema_utility"}

    user_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_user.user_id"), primary_key=True)
    cause_id: Mapped[int] = mapped_column(ForeignKey("schema_utility.table_blacklist_reason.cause_id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="blacklist")
    reason: Mapped["BlacklistReason"] = relationship(back_populates="blacklists")

