from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    AuthorizationCreate,
    AuthorizationResponse,
    CartAdd,
    CartQuantityChange,
    CartResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PermissionListResponse,
    RatingCreate,
    RatingResponse,
    RoleCreate,
    RoleResponse,
    UserCreate,
    UserDelete,
    UserResponse,
)
from models import Authorization, Blacklist, Permission, Rating, Role, User
from services.StockServices import StockService
from services.UserServices import CartService, RatingService, RolePermissionService, UserService

router = APIRouter(tags=["Users"])
rbac_router = APIRouter(prefix="/rbac", tags=["RBAC"])
cart_router = APIRouter(prefix="/users/{user_id}/cart", tags=["Cart"])
rating_router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = UserService.get_user_by_username(db, username=user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar.")

    return UserService.create_user(
        db=db,
        username=user_data.username,
        password_plain=user_data.password_plain,
        roles_id=user_data.roles_id,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, username=payload.username)
    if not user or not UserService.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password tidak valid.")

    blacklisted = db.scalars(
        select(Blacklist).where(Blacklist.user_id == user.user_id, Blacklist.deleted_at == None)
    ).first()
    if blacklisted:
        raise HTTPException(status_code=403, detail="Akun ini sedang diblokir.")

    role = db.get(Role, user.roles_id)
    return {
        "user_id": user.user_id,
        "username": user.username,
        "roles_id": user.roles_id,
        "role_description": role.roles_description if role else "Member",
    }


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return user


@router.get("/users/by-username/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return user


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, payload: UserDelete, db: Session = Depends(get_db)):
    deleted = UserService.soft_delete_user(db=db, user_id=user_id, deleted_by=payload.deleted_by)
    if not deleted:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    return {"status": "success", "message": "User berhasil dihapus secara soft delete."}


@router.get("/users")
def list_users(limit: int = 100, db: Session = Depends(get_db)):
    statement = (
        select(User)
        .where(User.deleted_at == None)
        .order_by(User.user_id.desc())
        .limit(limit)
    )
    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "roles_id": user.roles_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
        for user in db.scalars(statement).all()
    ]


@rbac_router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    return RolePermissionService.create_role(
        db=db,
        roles_name=payload.roles_name,
        description=payload.roles_description,
        deleted_by=payload.deleted_by,
    )


@rbac_router.get("/roles", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    statement = select(Role).where(Role.deleted_at == None).order_by(Role.roles_id)
    return list(db.scalars(statement).all())


@rbac_router.get("/roles/{roles_id}", response_model=RoleResponse)
def get_role(roles_id: int, db: Session = Depends(get_db)):
    role = db.get(Role, roles_id)
    if not role or role.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Role tidak ditemukan.")
    return role


@rbac_router.get("/permissions")
def list_permissions(db: Session = Depends(get_db)):
    statement = select(Permission).where(Permission.deleted_at == None).order_by(Permission.permission_id)
    return [
        {
            "permission_id": permission.permission_id,
            "permission_description": permission.permission_description,
        }
        for permission in db.scalars(statement).all()
    ]


@rbac_router.get("/roles/{roles_id}/permissions")
def get_role_permissions(roles_id: int, db: Session = Depends(get_db)):
    statement = (
        select(Authorization, Permission)
        .join(Permission, Authorization.permission_id == Permission.permission_id)
        .where(
            Authorization.roles_id == roles_id,
            Authorization.deleted_at == None,
            Permission.deleted_at == None,
        )
        .order_by(Permission.permission_id)
    )
    return [
        {
            "roles_id": authorization.roles_id,
            "permission_id": permission.permission_id,
            "permission_description": permission.permission_description,
        }
        for authorization, permission in db.execute(statement).all()
    ]


@rbac_router.get("/roles-permissions")
def role_permission_matrix(db: Session = Depends(get_db)):
    statement = (
        select(Role, Permission)
        .join(Authorization, Authorization.roles_id == Role.roles_id, isouter=True)
        .join(Permission, Permission.permission_id == Authorization.permission_id, isouter=True)
        .where(Role.deleted_at == None)
        .order_by(Role.roles_id, Permission.permission_id)
    )
    return [
        {
            "roles_id": role.roles_id,
            "roles_description": role.roles_description,
            "permission_id": permission.permission_id if permission else None,
            "permission_description": permission.permission_description if permission else None,
        }
        for role, permission in db.execute(statement).all()
    ]


@rbac_router.post(
    "/authorizations",
    response_model=AuthorizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_permission_to_role(payload: AuthorizationCreate, db: Session = Depends(get_db)):
    return RolePermissionService.assign_permission_to_role(
        db=db,
        roles_id=payload.roles_id,
        permission_id=payload.permission_id,
        deleted_by=payload.deleted_by,
    )


@rbac_router.get("/users/{user_id}/permissions", response_model=PermissionListResponse)
def get_user_permissions(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    permissions = RolePermissionService.get_user_permissions(db=db, user_id=user_id)
    return {"user_id": user_id, "permissions": permissions}


@cart_router.post("", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(user_id: int, cart_data: CartAdd, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    stock = StockService.get_stock_by_id(db, stock_id=cart_data.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan.")

    if cart_data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity harus lebih dari 0.")

    if stock.stock_quantity < cart_data.quantity:
        raise HTTPException(status_code=400, detail=f"Stok tidak mencukupi. Sisa stok: {stock.stock_quantity}")

    return CartService.add_to_cart(
        db=db,
        user_id=user_id,
        stock_id=cart_data.stock_id,
        quantity=cart_data.quantity,
        deleted_by=user_id,
    )


@cart_router.get("")
def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    cart_items = CartService.get_cart_by_user(db, user_id=user_id)
    result = []
    for item in cart_items:
        product_detail = None
        if item.stock:
            product_detail = {
                "stock_id": item.stock.stock_id,
                "name": item.stock.stock_name,
                "price_per_item": item.stock.stock_price,
                "stock_quantity": item.stock.stock_quantity,
                "rating": item.stock.stock_rating,
                "description": item.stock.stock_description,
                "category_description": item.stock.subcategory.category.category_description if item.stock.subcategory and item.stock.subcategory.category else "-",
                "subcategory_description": item.stock.subcategory.subcategory_description if item.stock.subcategory else "-",
                "total_price": item.stock.stock_price * item.quantity,
            }
        result.append(
            {
                "cart_id": item.cart_id,
                "stock_id": item.stock_id,
                "quantity": item.quantity,
                "product_detail": product_detail,
            }
        )
    return {"user_id": user_id, "cart_items": result}


@cart_router.patch("/stocks/{stock_id}", response_model=MessageResponse)
def change_cart_quantity(user_id: int, stock_id: int, payload: CartQuantityChange, db: Session = Depends(get_db)):
    cart_items = CartService.get_cart_by_user(db, user_id=user_id)
    cart_item = next((item for item in cart_items if item.stock_id == stock_id and item.deleted_at is None), None)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item cart tidak ditemukan.")

    new_quantity = cart_item.quantity + payload.delta
    if new_quantity <= 0:
        CartService.remove_from_cart(db=db, cart_id=cart_item.cart_id, user_id=user_id)
        return {"status": "success", "message": "Item cart berhasil dihapus."}

    stock = StockService.get_stock_by_id(db, stock_id=stock_id)
    if stock and stock.stock_quantity < new_quantity:
        raise HTTPException(status_code=400, detail=f"Stok tidak mencukupi. Sisa stok: {stock.stock_quantity}")

    cart_item.quantity = new_quantity
    db.commit()
    return {"status": "success", "message": "Quantity cart berhasil diperbarui."}


@cart_router.delete("/stocks/{stock_id}", response_model=MessageResponse)
def remove_stock_from_cart(user_id: int, stock_id: int, db: Session = Depends(get_db)):
    cart_items = CartService.get_cart_by_user(db, user_id=user_id)
    cart_item = next((item for item in cart_items if item.stock_id == stock_id and item.deleted_at is None), None)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item cart tidak ditemukan.")
    CartService.remove_from_cart(db=db, cart_id=cart_item.cart_id, user_id=user_id)
    return {"status": "success", "message": "Item cart berhasil dihapus."}


@cart_router.delete("/{cart_id}", response_model=MessageResponse)
def remove_item_from_cart(user_id: int, cart_id: int, db: Session = Depends(get_db)):
    deleted = CartService.remove_from_cart(db=db, cart_id=cart_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item cart tidak ditemukan.")
    return {"status": "success", "message": "Item cart berhasil dihapus."}


@rating_router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(payload: RatingCreate, db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id=payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")

    stock = StockService.get_stock_by_id(db, stock_id=payload.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Barang tidak ditemukan.")

    if payload.rating < 0:
        raise HTTPException(status_code=400, detail="Rating tidak boleh negatif.")

    return RatingService.give_rating(
        db=db,
        user_id=payload.user_id,
        stock_id=payload.stock_id,
        rating_value=payload.rating,
        comment=payload.comment,
        deleted_by=payload.deleted_by,
    )


@rating_router.get("/stocks/{stock_id}")
def get_stock_ratings(stock_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Rating)
        .where(Rating.stock_id == stock_id, Rating.deleted_at == None)
        .order_by(Rating.created_at.desc())
    ).all()
    return [
        {
            "rating_id": row.rating_id,
            "user_id": row.user_id,
            "stock_id": row.stock_id,
            "rating": row.rating,
            "comment": row.comment,
            "created_at": row.created_at,
        }
        for row in rows
    ]


router.include_router(rbac_router)
router.include_router(cart_router)
router.include_router(rating_router)
