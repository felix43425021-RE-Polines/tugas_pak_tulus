# schemas.py
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class ORMBase(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True


# Schema untuk User
class UserCreate(BaseModel):
    username: str
    password_plain: str
    roles_id: int

class UserResponse(ORMBase):
    user_id: int
    username: str
    roles_id: int

class UserDelete(BaseModel):
    deleted_by: int

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: int
    username: str
    roles_id: int
    role_description: Optional[str] = None

# Schema untuk Stock
class StockCreate(BaseModel):
    stock_name: str
    stock_subcategory: int
    stock_quantity: int
    stock_price: int
    stock_description: Optional[str] = None

class StockResponse(ORMBase):
    stock_id: int
    stock_name: str
    stock_subcategory: int
    stock_description: Optional[str] = None
    stock_quantity: int
    stock_price: int

class StockQuantityUpdate(BaseModel):
    items_sold: int

class StockCatalogResponse(StockResponse):
    stock_rating: Optional[float] = None
    category_id: Optional[int] = None
    category_description: Optional[str] = None
    subcategory_id: Optional[int] = None
    subcategory_description: Optional[str] = None

# Schema untuk Cart
class CartAdd(BaseModel):
    stock_id: int
    quantity: int

class CartQuantityChange(BaseModel):
    delta: int

class CartResponse(ORMBase):
    cart_id: int
    user_id: int
    stock_id: int
    quantity: int

class CartItemDetail(BaseModel):
    cart_id: int
    quantity: int
    product_detail: dict

class UserCartResponse(BaseModel):
    user_id: int
    cart_items: List[CartItemDetail]


# Schema untuk Role, Permission, dan Authorization
class RoleCreate(BaseModel):
    roles_name: str
    roles_description: Optional[str] = None
    deleted_by: int

class RoleResponse(ORMBase):
    roles_id: int
    roles_name: str
    roles_description: Optional[str] = None

class AuthorizationCreate(BaseModel):
    roles_id: int
    permission_id: int
    deleted_by: int

class AuthorizationResponse(ORMBase):
    authorization_id: int
    roles_id: int
    permission_id: int

class PermissionListResponse(BaseModel):
    user_id: int
    permissions: List[str]


# Schema untuk Rating
class RatingCreate(BaseModel):
    user_id: int
    stock_id: int
    rating: int
    comment: Optional[str] = None
    deleted_by: int

class RatingResponse(ORMBase):
    rating_id: int
    user_id: int
    stock_id: int
    rating: int
    comment: Optional[str] = None


# Schema untuk Category dan Subcategory
class CategoryCreate(BaseModel):
    category_name: str
    category_description: Optional[str] = None

class CategoryResponse(ORMBase):
    category_id: int
    category_name: str
    category_description: Optional[str] = None

class SubcategoryCreate(BaseModel):
    category_id: int
    subcategory_name: str
    subcategory_description: Optional[str] = None

class SubcategoryResponse(ORMBase):
    subcategory_id: int
    category_id: int
    subcategory_name: str
    subcategory_description: Optional[str] = None


# Schema untuk Utility
class ActivityCreate(BaseModel):
    description: Optional[str] = None
    deleted_by: int

class ActivityResponse(ORMBase):
    activity_id: int
    description: Optional[str] = None

class LogCreate(BaseModel):
    user_id: int
    activity_id: int

class LogResponse(ORMBase):
    log_id: int
    user_id: int
    activity_id: int
    created_at: datetime

class BlacklistReasonCreate(BaseModel):
    cause_name: str
    reason: Optional[str] = None
    deleted_by: int

class BlacklistReasonResponse(ORMBase):
    cause_id: int
    cause_name: str
    reason: Optional[str] = None

class BlacklistCreate(BaseModel):
    user_id: int
    cause_id: int
    deleted_by: int

class BlacklistResponse(ORMBase):
    user_id: int
    cause_id: int

class BlacklistStatusResponse(BaseModel):
    user_id: int
    is_blacklisted: bool

class MessageResponse(BaseModel):
    status: str
    message: str
