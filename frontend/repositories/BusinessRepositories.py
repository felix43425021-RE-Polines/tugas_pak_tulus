from repositories.ApiClient import ApiClient, ApiError


class RepositoryBase:
    client = ApiClient()
    _availability = None

    def __init__(self, database=None):
        self.database = database

    @property
    def connected(self):
        if RepositoryBase._availability is None:
            RepositoryBase._availability = self.client.is_available()
        return RepositoryBase._availability

    def _safe(self, default, callback):
        try:
            return callback()
        except ApiError as exc:
            if exc.status_code is None:
                RepositoryBase._availability = False
            return default

    def fetch_all(self, query, params=None):
        return []

    def fetch_one(self, query, params=None):
        return None

    def execute(self, query, params=None, commit=False):
        return None


class UserRepository(RepositoryBase):
    def login(self, username, password):
        return self._safe(
            None,
            lambda: self.client.post("/login", {"username": username, "password": password}),
        )

    def find_by_username(self, username):
        return self._safe(None, lambda: self.client.get(f"/users/by-username/{username}"))

    def find_by_id(self, user_id):
        return self._safe(None, lambda: self.client.get(f"/users/{user_id}"))

    def active_count(self):
        return len(self.list_users())

    def list_users(self, limit=100):
        return self._safe([], lambda: self.client.get("/users", {"limit": limit}))


class RoleRepository(RepositoryBase):
    def all_roles(self):
        return self._safe([], lambda: self.client.get("/rbac/roles"))

    def find_by_id(self, roles_id):
        return self._safe(None, lambda: self.client.get(f"/rbac/roles/{roles_id}"))

    def role_permission_matrix(self):
        return self._safe([], lambda: self.client.get("/rbac/roles-permissions"))


class PermissionRepository(RepositoryBase):
    def all_permissions(self):
        return self._safe([], lambda: self.client.get("/rbac/permissions"))


class AuthorizationRepository(RepositoryBase):
    def permissions_for_role(self, roles_id):
        return self._safe([], lambda: self.client.get(f"/rbac/roles/{roles_id}/permissions"))

    def roles_with_permissions(self):
        return self._safe([], lambda: self.client.get("/rbac/roles-permissions"))


class CategoryRepository(RepositoryBase):
    def all_categories(self):
        return self._safe([], lambda: self.client.get("/categories"))


class SubcategoryRepository(RepositoryBase):
    def by_category(self, category_id):
        return self._safe([], lambda: self.client.get("/subcategories", {"category_id": category_id}))


class StockRepository(RepositoryBase):
    def catalog(self, query_text="", category_description="Semua"):
        return self._safe(
            [],
            lambda: self.client.get(
                "/stocks/catalog",
                {"query": query_text, "category": category_description, "limit": 100},
            ),
        )

    def find_by_id(self, stock_id):
        return self._safe(None, lambda: self.client.get(f"/stocks/catalog/{stock_id}"))

    def categories(self):
        rows = self.catalog()
        categories = {}
        for row in rows:
            category_id = row.get("category_id")
            category_description = row.get("category_description")
            if category_description:
                categories[category_description] = {
                    "category_id": category_id,
                    "category_description": category_description,
                }
        return list(categories.values())

    def list_stock(self, limit=100):
        return self._safe([], lambda: self.client.get("/stocks/catalog", {"limit": limit}))


class CartRepository(RepositoryBase):
    def items_for_user(self, user_id):
        response = self._safe({}, lambda: self.client.get(f"/users/{user_id}/cart"))
        items = []
        for item in response.get("cart_items", []):
            product = item.get("product_detail") or {}
            items.append(
                {
                    "cart_id": item.get("cart_id"),
                    "user_id": user_id,
                    "stock_id": item.get("stock_id"),
                    "quantity": item.get("quantity", 0),
                    "stock_name": product.get("name"),
                    "stock_price": product.get("price_per_item", 0),
                    "stock_rating": product.get("rating", 0),
                    "stock_quantity": product.get("stock_quantity", 0),
                    "stock_description": product.get("description", ""),
                    "category_description": product.get("category_description", "-"),
                    "subcategory_description": product.get("subcategory_description", "-"),
                }
            )
        return items

    def add_or_increment(self, user_id, stock_id, quantity=1, deleted_by=0):
        return self._safe(
            None,
            lambda: self.client.post(
                f"/users/{user_id}/cart",
                {"stock_id": stock_id, "quantity": quantity},
            ),
        )

    def change_quantity(self, user_id, stock_id, delta):
        return self._safe(
            None,
            lambda: self.client.patch(f"/users/{user_id}/cart/stocks/{stock_id}", {"delta": delta}),
        )

    def remove(self, user_id, stock_id):
        return self._safe(None, lambda: self.client.delete(f"/users/{user_id}/cart/stocks/{stock_id}"))


class RatingRepository(RepositoryBase):
    def ratings_for_stock(self, stock_id):
        return self._safe([], lambda: self.client.get(f"/ratings/stocks/{stock_id}"))


class ActivityRepository(RepositoryBase):
    def all_activity(self):
        return self._safe([], lambda: self.client.get("/utility/activities"))


class LogRepository(RepositoryBase):
    def logs_for_user(self, user_id):
        return self._safe([], lambda: self.client.get(f"/utility/users/{user_id}/logs/detail"))

    def latest_logs(self, limit=100):
        return self._safe([], lambda: self.client.get("/utility/logs", {"limit": limit}))


class BlacklistReasonRepository(RepositoryBase):
    def all_reasons(self):
        return self._safe([], lambda: self.client.get("/utility/blacklist-reasons"))


class BlacklistRepository(RepositoryBase):
    def is_blacklisted(self, user_id):
        response = self._safe({"is_blacklisted": False}, lambda: self.client.get(f"/utility/blacklists/{user_id}/status"))
        return bool(response.get("is_blacklisted"))

    def all_blacklisted_users(self):
        return self._safe([], lambda: self.client.get("/utility/blacklists"))
