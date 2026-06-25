from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session
from models import Stock, Category, Subcategory

class StockService:
    """Service untuk mengelola tabel table_stock, table_category, dan table_subcategory"""

    # --- KATEGORI & SUB-KATEGORI ---
    @staticmethod
    def create_category(db: Session, description: str, category_name: str) -> Category:
        """Membuat kategori baru (e.g., Elektronik, Pakaian)"""
        new_category = Category(category_description=description, category_name=category_name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category

    @staticmethod
    def create_subcategory(db: Session, category_id: int, description: str, subcategory_name: str) -> Subcategory:
        """Membuat sub-kategori baru di bawah kategori tertentu"""
        new_sub = Subcategory(category_id=category_id, subcategory_description=description, subcategory_name=subcategory_name)
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        return new_sub

    # --- MANAGEMENT STOK BARANG ---
    @staticmethod
    def create_stock(db: Session, name: str, subcategory_id: int, quantity: int, price: int, deleted_by: int, description: Optional[str] = None) -> Stock:
        """Menambahkan stok barang baru ke dalam database"""
        new_stock = Stock(
            stock_name=name,
            stock_subcategory=subcategory_id,
            stock_quantity=quantity,
            stock_price=price,
            stock_description=description,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(new_stock)
        db.commit()
        db.refresh(new_stock)
        return new_stock

    @staticmethod
    def get_stock_by_id(db: Session, stock_id: int) -> Optional[Stock]:
        """Mengambil detail satu produk berdasarkan ID yang belum dihapus"""
        statement = select(Stock).where(Stock.stock_id == stock_id, Stock.deleted_at == None)
        return db.scalars(statement).first()

    @staticmethod
    def get_all_active_stocks(db: Session, skip: int = 0, limit: int = 20) -> List[Stock]:
        """Mengambil katalog semua produk aktif dengan fitur pagination"""
        statement = select(Stock).where(Stock.deleted_at == None).offset(skip).limit(limit)
        return list(db.scalars(statement).all())

    @staticmethod
    def update_stock_quantity(db: Session, stock_id: int, items_sold: int) -> bool:
        """Mengurangi atau menambah kuantitas stok barang (misal setelah dibeli)"""
        stock = db.get(Stock, stock_id)
        if stock and stock.stock_quantity >= items_sold:
            stock.stock_quantity -= items_sold
            stock.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False

    @staticmethod
    def soft_delete_stock(db: Session, stock_id: int, deleted_by: int) -> bool:
        """Menghapus barang secara halus (Soft Delete) dari katalog umum"""
        statement = (
            update(Stock)
            .where(Stock.stock_id == stock_id)
            .values(deleted_at=datetime.utcnow(), deleted_by=deleted_by)
        )
        result = db.execute(statement)
        db.commit()
        return result.rowcount > 0