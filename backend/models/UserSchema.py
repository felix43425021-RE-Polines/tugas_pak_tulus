from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class Role(Base):
    __tablename__ = "table_roles"
    __table_args__ = {"schema": "schema_user"}

    roles_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    roles_name: Mapped[str] = mapped_column(String(100))
    roles_description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="role")
    authorizations: Mapped[List["Authorization"]] = relationship(back_populates="role")


class Permission(Base):
    __tablename__ = "table_permission"
    __table_args__ = {"schema": "schema_user"}

    permission_id: Mapped[int] = mapped_column(primary_key=True)
    permission_description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    authorizations: Mapped[List["Authorization"]] = relationship(back_populates="permission")


class Authorization(Base):
    __tablename__ = "table_authorization"
    __table_args__ = {"schema": "schema_user"}

    authorization_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    roles_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_roles.roles_id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_permission.permission_id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="authorizations")
    permission: Mapped["Permission"] = relationship(back_populates="authorizations")


class User(Base):
    __tablename__ = "table_user"
    __table_args__ = {"schema": "schema_user"}

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), primary_key=True)
    password_hash: Mapped[str] = mapped_column(Text)
    roles_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_roles.roles_id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users")
    carts: Mapped[List["Cart"]] = relationship(back_populates="user")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="user")
    logs: Mapped[List["Log"]] = relationship(back_populates="user")
    blacklist: Mapped[Optional["Blacklist"]] = relationship(back_populates="user")


class Cart(Base):
    __tablename__ = "table_cart"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_positive"),
        {"schema": "schema_user"}
    )

    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_user.user_id"), primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("schema_stock.table_stock.stock_id"), primary_key=True)
    quantity: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    user: Mapped["User"] = relationship(back_populates="carts")
    stock: Mapped["Stock"] = relationship(back_populates="carts")


class Rating(Base):
    __tablename__ = "table_rating"
    __table_args__ = (
        CheckConstraint("rating >= 0", name="check_rating_positive"),
        {"schema": "schema_user"}
    )

    rating_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("schema_user.table_user.user_id"), primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("schema_stock.table_stock.stock_id"), primary_key=True)
    rating: Mapped[int] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    user: Mapped["User"] = relationship(back_populates="ratings")
    stock: Mapped["Stock"] = relationship(back_populates="ratings")
