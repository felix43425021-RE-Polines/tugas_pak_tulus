import hashlib
import hmac
import os
try:
    import bcrypt
except ImportError:
    bcrypt = None
from typing import List, Optional
from datetime import datetime
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session
from models import User, Role, Permission, Authorization, Cart, Rating
from models import User

class UserService:
    """Service untuk mengelola tabel table_user dengan enkripsi Bcrypt"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Mengubah password mentah menjadi hash bcrypt yang aman"""
        if bcrypt is not None:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_bytes = bcrypt.hashpw(password_bytes, salt)
            return hashed_bytes.decode('utf-8')

        iterations = 260000
        salt = os.urandom(16).hex()
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()
        return f"pbkdf2_sha256${iterations}${salt}${digest}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Mengecek apakah password mentah cocok dengan hash di database (untuk Login)"""
        if not hashed_password:
            return False

        hashed_password = str(hashed_password)

        if hashed_password.startswith("sha256$"):
            expected = hashed_password.split("$", 1)[1]
            digest = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
            return hmac.compare_digest(digest, expected)

        if hashed_password.startswith("pbkdf2_sha256$"):
            parts = hashed_password.split("$")
            if len(parts) != 4:
                return False
            _, iterations, salt, expected = parts
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations),
            ).hex()
            return hmac.compare_digest(derived, expected)

        if hashed_password.startswith("plain$"):
            expected = hashed_password.split("$", 1)[1]
            return hmac.compare_digest(plain_password, expected)

        if bcrypt is not None:
            try:
                return bcrypt.checkpw(
                    plain_password.encode('utf-8'), 
                    hashed_password.encode('utf-8')
                )
            except Exception:
                pass

        return hmac.compare_digest(plain_password, hashed_password)

    @staticmethod
    def create_user(db: Session, username: str, password_plain: str, roles_id: int) -> User:
        """Membuat user baru dengan password yang otomatis di-hash menggunakan Bcrypt"""
        
        # 1. Enkripsi password mentah sebelum masuk database
        secure_hash = UserService.hash_password(password_plain)
        
        # 2. Buat objek objek model User
        new_user = User(
            username=username,
            password_hash=secure_hash,  # Menyimpan hasil hash bcrypt
            roles_id=roles_id,
            created_at=datetime.utcnow()
        )
        
        # 3. Simpan ke database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Mencari user berdasarkan ID"""
        statement = select(User).where(User.user_id == user_id, User.deleted_at == None)
        return db.scalars(statement).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Mencari user berdasarkan Username (untuk login)"""
        statement = select(User).where(User.username == username, User.deleted_at == None)
        return db.scalars(statement).first()

    @staticmethod
    def soft_delete_user(db: Session, user_id: int, deleted_by: int) -> bool:
        """Menghapus user secara aman (Soft Delete) tanpa membuang data dari DB"""
        statement = (
            update(User)
            .where(User.user_id == user_id)
            .values(deleted_at=datetime.utcnow(), deleted_by=deleted_by)
        )
        result = db.execute(statement)
        db.commit()
        return result.rowcount > 0
    
class RolePermissionService:
    """Service untuk mengelola Roles, Permissions, dan Authorization (RBAC)"""

    @staticmethod
    def create_role(db: Session, roles_name: str, description: str, deleted_by: int) -> Role:
        """Membuat Role Baru (e.g., Admin, Customer)"""
        new_role = Role(
            roles_name=roles_name,
            roles_description=description,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role

    @staticmethod
    def assign_permission_to_role(db: Session, roles_id: int, permission_id: int, deleted_by: int) -> Authorization:
        """Menghubungkan Role dengan Permission (Tabel Authorization)"""
        auth = Authorization(
            roles_id=roles_id,
            permission_id=permission_id,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(auth)
        db.commit()
        db.refresh(auth)
        return auth

    @staticmethod
    def get_user_permissions(db: Session, user_id: int) -> List[str]:
        """Mengambil semua daftar izin (permissions) yang dimiliki oleh seorang user"""
        # Melakukan JOIN antara User -> Role -> Authorization -> Permission
        statement = (
            select(Permission.permission_description)
            .join(Authorization, Permission.permission_id == Authorization.permission_id)
            .join(Role, Authorization.roles_id == Role.roles_id)
            .join(User, Role.roles_id == User.roles_id)
            .where(User.user_id == user_id)
        )
        return list(db.scalars(statement).all())


class CartService:
    """Service untuk mengelola Keranjang Belanja (table_cart)"""

    @staticmethod
    def add_to_cart(db: Session, user_id: int, stock_id: int, quantity: int, deleted_by: int) -> Cart:
        """Menambahkan barang ke keranjang atau mengupdate jumlah jika sudah ada"""
        # Cek apakah barang yang sama sudah ada di keranjang user tersebut
        statement = select(Cart).where(Cart.user_id == user_id, Cart.stock_id == stock_id)
        existing_item = db.scalars(statement).first()

        if existing_item:
            existing_item.quantity += quantity
            existing_item.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            new_cart_item = Cart(
                user_id=user_id,
                stock_id=stock_id,
                quantity=quantity,
                created_at=datetime.utcnow(),
                deleted_by=deleted_by
            )
            db.add(new_cart_item)
            db.commit()
            db.refresh(new_cart_item)
            return new_cart_item

    @staticmethod
    def get_cart_by_user(db: Session, user_id: int) -> List[Cart]:
        """Melihat semua isi keranjang milik user beserta informasi barangnya (Lintas Skema)"""
        statement = select(Cart).where(Cart.user_id == user_id)
        return list(db.scalars(statement).all())

    @staticmethod
    def remove_from_cart(db: Session, cart_id: int, user_id: int) -> bool:
        """Menghapus item tertentu dari keranjang belanja"""
        statement = delete(Cart).where(Cart.cart_id == cart_id, Cart.user_id == user_id)
        result = db.execute(statement)
        db.commit()
        return result.rowcount > 0


class RatingService:
    """Service untuk mengelola Ulasan / Rating Produk (table_rating)"""

    @staticmethod
    def give_rating(db: Session, user_id: int, stock_id: int, rating_value: int, comment: str, deleted_by: int) -> Rating:
        """Memberikan rating pada suatu produk"""
        new_rating = Rating(
            user_id=user_id,
            stock_id=stock_id,
            rating=rating_value,
            comment=comment,
            created_at=datetime.utcnow(),
            deleted_by=deleted_by
        )
        db.add(new_rating)
        db.commit()
        db.refresh(new_rating)
        return new_rating
