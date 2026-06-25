from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    CategoryCreate,
    CategoryResponse,
    MessageResponse,
    StockCreate,
    StockCatalogResponse,
    StockQuantityUpdate,
    StockResponse,
    SubcategoryCreate,
    SubcategoryResponse,
)
from models import Category, Stock, Subcategory
from services.StockServices import StockService

router = APIRouter(tags=["Stocks"])


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    return StockService.create_category(
        db=db,
        category_name=payload.category_name,
        description=payload.category_description,
    )


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    statement = select(Category).order_by(Category.category_id)
    return list(db.scalars(statement).all())


@router.post("/subcategories", response_model=SubcategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(payload: SubcategoryCreate, db: Session = Depends(get_db)):
    return StockService.create_subcategory(
        db=db,
        category_id=payload.category_id,
        subcategory_name=payload.subcategory_name,
        description=payload.subcategory_description,
    )


@router.get("/subcategories", response_model=List[SubcategoryResponse])
def get_subcategories(category_id: int | None = None, db: Session = Depends(get_db)):
    statement = select(Subcategory)
    if category_id is not None:
        statement = statement.where(Subcategory.category_id == category_id)
    return list(db.scalars(statement.order_by(Subcategory.subcategory_id)).all())


@router.post("/stocks", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)):
    return StockService.create_stock(
        db=db,
        name=stock_data.stock_name,
        subcategory_id=stock_data.stock_subcategory,
        quantity=stock_data.stock_quantity,
        price=stock_data.stock_price,
        description=stock_data.stock_description,
        deleted_by=1,
    )


def _stock_catalog_row(stock: Stock):
    subcategory = stock.subcategory
    category = subcategory.category if subcategory else None
    return {
        "stock_id": stock.stock_id,
        "stock_name": stock.stock_name,
        "stock_subcategory": stock.stock_subcategory,
        "stock_rating": stock.stock_rating,
        "stock_description": stock.stock_description,
        "stock_quantity": stock.stock_quantity,
        "stock_price": stock.stock_price,
        "category_id": category.category_id if category else None,
        "category_description": category.category_description if category else None,
        "subcategory_id": subcategory.subcategory_id if subcategory else None,
        "subcategory_description": subcategory.subcategory_description if subcategory else None,
    }


@router.get("/stocks/catalog", response_model=List[StockCatalogResponse])
def get_stock_catalog(
    query: str = "",
    category: str = "Semua",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    statement = (
        select(Stock)
        .join(Subcategory, Stock.stock_subcategory == Subcategory.subcategory_id)
        .join(Category, Subcategory.category_id == Category.category_id)
        .where(Stock.deleted_at == None)
        .order_by(Stock.stock_name)
        .offset(skip)
        .limit(limit)
    )
    stocks = list(db.scalars(statement).unique().all())
    query_text = query.strip().lower()
    category_text = (category or "Semua").strip()
    result = []
    for stock in stocks:
        row = _stock_catalog_row(stock)
        if category_text not in ("", "Semua") and row["category_description"] != category_text:
            continue
        haystack = " ".join(
            str(row.get(key) or "")
            for key in ("stock_name", "stock_description", "category_description", "subcategory_description")
        ).lower()
        if query_text and query_text not in haystack:
            continue
        result.append(row)
    return result


@router.get("/stocks/catalog/{stock_id}", response_model=StockCatalogResponse)
def get_stock_catalog_detail(stock_id: int, db: Session = Depends(get_db)):
    stock = StockService.get_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan.")
    return _stock_catalog_row(stock)


@router.get("/stocks", response_model=List[StockResponse])
def get_stocks(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return StockService.get_all_active_stocks(db=db, skip=skip, limit=limit)


@router.get("/stocks/{stock_id}", response_model=StockResponse)
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = StockService.get_stock_by_id(db=db, stock_id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan.")
    return stock


@router.patch("/stocks/{stock_id}/quantity", response_model=MessageResponse)
def update_stock_quantity(stock_id: int, payload: StockQuantityUpdate, db: Session = Depends(get_db)):
    if payload.items_sold <= 0:
        raise HTTPException(status_code=400, detail="Jumlah barang harus lebih dari 0.")

    updated = StockService.update_stock_quantity(
        db=db,
        stock_id=stock_id,
        items_sold=payload.items_sold,
    )
    if not updated:
        raise HTTPException(status_code=400, detail="Barang tidak ditemukan atau stok tidak mencukupi.")
    return {"status": "success", "message": "Quantity stok berhasil diperbarui."}


@router.delete("/stocks/{stock_id}", response_model=MessageResponse)
def delete_stock(stock_id: int, deleted_by: int, db: Session = Depends(get_db)):
    deleted = StockService.soft_delete_stock(db=db, stock_id=stock_id, deleted_by=deleted_by)
    if not deleted:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan.")
    return {"status": "success", "message": "Stok berhasil dihapus secara soft delete."}
