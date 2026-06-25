from repositories.BusinessFactory import BusinessFactory
import hashlib
import hmac


class TokokitaModel:
    def __init__(self):
        self.factory = BusinessFactory()
        self.user_repo = self.factory.user()
        self.stock_repo = self.factory.stock()
        self.cart_repo = self.factory.cart()
        self.role_repo = self.factory.role()
        self.permission_repo = self.factory.permission()
        self.authorization_repo = self.factory.authorization()
        self.rating_repo = self.factory.rating()
        self.category_repo = self.factory.category()
        self.subcategory_repo = self.factory.subcategory()
        self.activity_repo = self.factory.activity()
        self.log_repo = self.factory.log()
        self.blacklist_repo = self.factory.blacklist()
        self.blacklist_reason_repo = self.factory.blacklist_reason()

        self.user = {
            "user_id": None,
            "name": "Tamu",
            "email": "",
            "roles_id": None,
            "role_description": "Guest",
        }
        self.logged_in = False
        self.selected_product_id = None
        self._memory_cart = {}
        self._memory_products = [
            {
                "id": 1,
                "name": "Modern Mountain Coffee Maker",
                "category": "Dapur",
                "subcategory": "Coffee",
                "price": 250000,
                "stock": 12,
                "description": "Mesin kopi compact untuk penggunaan harian di rumah.",
                "rating": 4.5,
            },
            {
                "id": 2,
                "name": "Wireless Headphones",
                "category": "Elektronik",
                "subcategory": "Audio",
                "price": 250000,
                "stock": 8,
                "description": "Headphone ringan dengan suara jernih dan baterai tahan lama.",
                "rating": 4.7,
            },
            {
                "id": 3,
                "name": "Minimalist Daily Backpack - Gray",
                "category": "Fashion",
                "subcategory": "Bag",
                "price": 250000,
                "stock": 15,
                "description": "Tas harian minimalis untuk kerja, kuliah, dan jalan santai.",
                "rating": 4.5,
            },
            {
                "id": 4,
                "name": "Desk Lamp Soft Light",
                "category": "Rumah",
                "subcategory": "Lamp",
                "price": 120000,
                "stock": 20,
                "description": "Lampu meja dengan cahaya lembut untuk belajar dan bekerja.",
                "rating": 4.4,
            },
            {
                "id": 5,
                "name": "Smart Bottle",
                "category": "Lifestyle",
                "subcategory": "Bottle",
                "price": 98000,
                "stock": 30,
                "description": "Botol minum sederhana yang cocok untuk aktivitas harian.",
                "rating": 4.2,
            },
            {
                "id": 6,
                "name": "Ergonomic Mouse",
                "category": "Elektronik",
                "subcategory": "Accessory",
                "price": 175000,
                "stock": 9,
                "description": "Mouse nyaman dipakai lama untuk kerja dan belajar.",
                "rating": 4.6,
            },
        ]

    def _verify_password(self, raw_password, stored_hash):
        if stored_hash is None:
            return False

        stored_hash = str(stored_hash)

        if stored_hash.startswith("sha256$"):
            expected = stored_hash.split("$", 1)[1]
            digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
            return hmac.compare_digest(digest, expected)

        if stored_hash.startswith("pbkdf2_sha256$"):
            # Format: pbkdf2_sha256$<iterations>$<salt>$<hash_hex>
            parts = stored_hash.split("$")
            if len(parts) != 4:
                return False
            _, iterations, salt, expected = parts
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                raw_password.encode("utf-8"),
                salt.encode("utf-8"),
                int(iterations),
            ).hex()
            return hmac.compare_digest(derived, expected)

        if stored_hash.startswith("plain$"):
            expected = stored_hash.split("$", 1)[1]
            return hmac.compare_digest(raw_password, expected)

        # Backward compatibility for legacy plain text rows.
        return hmac.compare_digest(raw_password, stored_hash)

    def _normalize_product(self, row):
        if row is None:
            return None
        return {
            "id": row.get("stock_id", row.get("id")),
            "name": row.get("stock_name", row.get("name")),
            "category": row.get("category_description", row.get("category", "-")),
            "subcategory": row.get("subcategory_description", row.get("subcategory", "-")),
            "price": int(row.get("stock_price", row.get("price", 0)) or 0),
            "stock": int(row.get("stock_quantity", row.get("stock", 0)) or 0),
            "description": row.get("stock_description", row.get("description", "")),
            "rating": float(row.get("stock_rating", row.get("rating", 0)) or 0),
            "raw": row,
        }

    def authenticate(self, username, password):
        if not username.strip() or not password.strip():
            return False, "Username dan password harus diisi."

        credential = username.strip()
        fallback_username = credential.split("@")[0]
        user_row = self.user_repo.login(credential, password)
        if user_row is None and "@" in credential:
            user_row = self.user_repo.login(fallback_username, password)
        
        if user_row is None:
            if self.user_repo.connected:
                return False, "Username atau password tidak valid."
            self.user = {
                "user_id": 1,
                "name": fallback_username.replace(".", " ").title() or "Tamu",
                "username": fallback_username.replace(".", " ").title() or "Tamu",
                "email": credential,
                "roles_id": 1,
                "role_description": "Guest",
            }
            self.logged_in = True
            return True, f"Selamat datang, {self.user['name']}"

        display_name = user_row["username"].replace(".", " ").title()
        self.user = {
            "user_id": user_row["user_id"],
            "name": display_name,
            "username": display_name,
            "email": credential,
            "roles_id": user_row["roles_id"],
            "role_description": user_row.get("role_description") or "Member",
        }
        self.logged_in = True
        return True, f"Selamat datang, {self.user['name']}"

    def can_access_admin(self):
        if not self.logged_in:
            return False

        role_text = (self.user.get("role_description") or "").lower()
        if "admin" in role_text:
            return True

        permissions = self.user_permissions()
        for permission in permissions:
            text = str(permission.get("permission_description") or "").lower()
            if "admin" in text or "manage" in text:
                return True
        return False

    def admin_snapshot(self, limit=100):
        return {
            "db_connected": self.user_repo.connected,
            "users": self.user_repo.list_users(limit=limit),
            "stock": self.stock_repo.list_stock(limit=limit),
            "roles_permissions": self.role_repo.role_permission_matrix(),
            "permissions": self.permission_repo.all_permissions(),
            "blacklist": self.blacklisted_users(),
            "reasons": self.blacklist_reasons(),
            "logs": self.log_repo.latest_logs(limit=limit),
            "activities": self.activities(),
        }

    def logout(self):
        self.logged_in = False
        self.user = {
            "user_id": None,
            "username": "Tamu",
            "roles_id": None,
            "role_description": "Guest",
        }
        self.selected_product_id = None

    def categories(self):
        rows = self.stock_repo.categories()
        if rows:
            return ["Semua"] + [row["category_description"] for row in rows]

        rows = self.category_repo.all_categories()
        return ["Semua"] + [row["category_description"] for row in rows]

    def search_products(self, query="", category="Semua"):
        rows = self.stock_repo.catalog(query_text=query, category_description=category)
        if rows:
            return [self._normalize_product(row) for row in rows]

        query = query.lower().strip()
        filtered = []
        for product in self._memory_products:
            if category not in (None, "", "Semua") and product["category"] != category:
                continue
            haystack = f"{product['name']} {product['category']} {product['subcategory']} {product['description']}".lower()
            if query and query not in haystack:
                continue
            filtered.append(self._normalize_product(product))
        return filtered

    def get_product(self, product_id):
        row = self.stock_repo.find_by_id(product_id)
        if row is not None:
            return self._normalize_product(row)

        for product in self._memory_products:
            if product["id"] == product_id:
                return self._normalize_product(product)
        return None

    def select_product(self, product_id):
        self.selected_product_id = product_id

    def selected_product(self):
        if self.selected_product_id is None:
            return None
        return self.get_product(self.selected_product_id)

    def add_to_cart(self, product_id, quantity=1):
        if self.logged_in and self.user.get("user_id") is not None and self.stock_repo.find_by_id(product_id) is not None:
            self.cart_repo.add_or_increment(
                self.user["user_id"],
                product_id,
                quantity=quantity,
                deleted_by=self.user["user_id"] or 0,
            )
            return

        current_quantity = self._memory_cart.get(product_id, 0)
        self._memory_cart[product_id] = current_quantity + quantity

    def change_cart_quantity(self, product_id, delta):
        if self.logged_in and self.user.get("user_id") is not None and self.stock_repo.find_by_id(product_id) is not None:
            self.cart_repo.change_quantity(self.user["user_id"], product_id, delta)
            return

        current_quantity = self._memory_cart.get(product_id, 0) + delta
        if current_quantity <= 0:
            self._memory_cart.pop(product_id, None)
        else:
            self._memory_cart[product_id] = current_quantity

    def remove_from_cart(self, product_id):
        if self.logged_in and self.user.get("user_id") is not None:
            self.cart_repo.remove(self.user["user_id"], product_id)
            return

        self._memory_cart.pop(product_id, None)

    def cart_items(self):
        if self.logged_in and self.user.get("user_id") is not None:
            rows = self.cart_repo.items_for_user(self.user["user_id"])
            items = []
            for row in rows:
                product = self._normalize_product(row)
                items.append(
                    {
                        "product": product,
                        "quantity": row["quantity"],
                        "subtotal": int(row["quantity"]) * int(row["stock_price"]),
                    }
                )
            return items

        items = []
        for product_id, quantity in self._memory_cart.items():
            product = self.get_product(product_id)
            if product is None:
                continue
            items.append({"product": product, "quantity": quantity, "subtotal": product["price"] * quantity})
        return items

    def cart_total(self):
        return sum(item["subtotal"] for item in self.cart_items())

    def roles(self):
        return self.role_repo.all_roles()

    def permissions(self):
        return self.permission_repo.all_permissions()

    def user_permissions(self):
        if self.user.get("roles_id") is None:
            return []
        return self.authorization_repo.permissions_for_role(self.user["roles_id"])

    def ratings_for_selected_product(self):
        if self.selected_product_id is None:
            return []
        return self.rating_repo.ratings_for_stock(self.selected_product_id)

    def blacklist_reasons(self):
        return self.blacklist_reason_repo.all_reasons()

    def blacklisted_users(self):
        return self.blacklist_repo.all_blacklisted_users()

    def activities(self):
        return self.activity_repo.all_activity()

    def logs(self):
        if self.user.get("user_id") is None:
            return []
        return self.log_repo.logs_for_user(self.user["user_id"])

    @staticmethod
    def format_price(value):
        return f"Rp {int(value):,}".replace(",", ".")
