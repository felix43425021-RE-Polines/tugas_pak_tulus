from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .Base import Base

class Category(Base):
    __tablename__ = "table_category"
    __table_args__ = {"schema": "schema_stock"}

    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    category_description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    subcategories: Mapped[List["Subcategory"]] = relationship(back_populates="category")


class Subcategory(Base):
    __tablename__ = "table_subcategory"
    __table_args__ = {"schema": "schema_stock"}

    subcategory_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subcategory_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("schema_stock.table_category.category_id"), primary_key=True)
    subcategory_description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    category: Mapped["Category"] = relationship(back_populates="subcategories")
    stocks: Mapped[List["Stock"]] = relationship(back_populates="subcategory")


class Stock(Base):
    __tablename__ = "table_stock"
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="check_stock_quantity_positive"),
        CheckConstraint("stock_price >= 0", name="check_stock_price_positive"),
        {"schema": "schema_stock"}
    )

    stock_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_name: Mapped[str] = mapped_column(String(100))
    stock_subcategory: Mapped[int] = mapped_column(ForeignKey("schema_stock.table_subcategory.subcategory_id"))
    stock_rating: Mapped[Optional[float]] = mapped_column()
    stock_description: Mapped[Optional[str]] = mapped_column(Text)
    stock_quantity: Mapped[int] = mapped_column()
    stock_price: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column()
    deleted_by: Mapped[Optional[int]] = mapped_column()

    # Relationships
    subcategory: Mapped["Subcategory"] = relationship(back_populates="stocks")
    carts: Mapped[List["Cart"]] = relationship(back_populates="stock")
    ratings: Mapped[List["Rating"]] = relationship(back_populates="stock")
