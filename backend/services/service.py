# services.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
# Import model dari package models yang sudah kita buat sebelumnya
from models import User, Stock, Cart, Log

class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Mengambil satu user berdasarkan ID"""
        # SQLAlchemy 2.0 menggunakan select() dan db.scalars()
        statement = select(User).where(User.user_id == user_id)
        return db.scalars(statement).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 10) -> List[User]:
        """Mengambil semua user dengan fitur pagination (offset & limit)"""
        statement = select(User).offset(skip).limit(limit)
        return list(db.scalars(statement).all())


class StockService:
    @staticmethod
    def get_stock_by_id(db: Session, stock_id: int) -> Optional[Stock]:
        """Mengambil data stok barang berdasarkan ID"""
        statement = select(Stock).where(Stock.stock_id == stock_id)
        return db.scalars(statement).first()


class CartService:
    @staticmethod
    def get_user_cart_items(db: Session, user_id: int) -> List[Cart]:
        """Mengambil semua isi keranjang milik user tertentu (Lintas Skema)"""
        # Karena relasi sudah diatur, kita bisa otomatis melakukan join atau 
        # membaca properti relasi nantinya setelah data Cart diambil.
        statement = select(Cart).where(Cart.user_id == user_id)
        return list(db.scalars(statement).all())