from frontend.Database import Database


class RepositoryBase:
    def __init__(self, database=None):
        self.database = database or Database()

    @property
    def connected(self):
        return getattr(self.database, "connected", False)

    def fetch_all(self, query, params=None):
        if not self.connected:
            return []
        self.database.cursor.execute(query, params or ())
        return self.database.cursor.fetchall()

    def fetch_one(self, query, params=None):
        if not self.connected:
            return None
        self.database.cursor.execute(query, params or ())
        return self.database.cursor.fetchone()

    def execute(self, query, params=None, commit=False):
        if not self.connected:
            return None
        self.database.cursor.execute(query, params or ())
        if commit:
            self.database.db.commit()
        return self.database.cursor.rowcount


class UserRepository(RepositoryBase):
    table = "schema_user.table_user"

    def find_by_username(self, username):
        return self.fetch_one(
            f"""
            SELECT user_id, username, password_hash, roles_id
            FROM `{self.table}`
            WHERE username = %s AND deleted_at IS NULL
            """,
            (username,),
        )

    def find_by_id(self, user_id):
        return self.fetch_one(
            f"""
            SELECT user_id, username, password_hash, roles_id
            FROM {self.table}
            WHERE user_id = %s AND deleted_at IS NULL
            """,
            (user_id,),
        )

    def active_count(self):
        row = self.fetch_one(
            f"SELECT COUNT(*) AS total FROM {self.table} WHERE deleted_at IS NULL"
        )
        return int(row["total"] if row else 0)

    def list_users(self, limit=100):
        return self.fetch_all(
            f"""
            SELECT user_id, username, roles_id, created_at, updated_at
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY user_id DESC
            LIMIT %s
            """,
            (limit,),
        )


class RoleRepository(RepositoryBase):
    table = "schema_user.table_roles"

    def all_roles(self):
        return self.fetch_all(
            f"""
            SELECT roles_id, roles_description
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY roles_id
            """
        )

    def find_by_id(self, roles_id):
        return self.fetch_one(
            f"""
            SELECT roles_id, roles_description
            FROM {self.table}
            WHERE roles_id = %s AND deleted_at IS NULL
            """,
            (roles_id,),
        )

    def role_permission_matrix(self):
        return self.fetch_all(
            """
            SELECT r.roles_id, r.roles_description, p.permission_id, p.permission_description
            FROM schema_user.table_roles r
            LEFT JOIN schema_user.table_authorization a ON a.roles_id = r.roles_id AND a.deleted_at IS NULL
            LEFT JOIN schema_user.table_permission p ON p.permission_id = a.permission_id AND p.deleted_at IS NULL
            WHERE r.deleted_at IS NULL
            ORDER BY r.roles_id, p.permission_id
            """
        )


class PermissionRepository(RepositoryBase):
    table = "schema_user.table_permission"

    def all_permissions(self):
        return self.fetch_all(
            f"""
            SELECT permission_id, permission_description
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY permission_id
            """
        )


class AuthorizationRepository(RepositoryBase):
    table = "schema_user.table_authorization"

    def permissions_for_role(self, roles_id):
        return self.fetch_all(
            f"""
            SELECT a.roles_id, p.permission_id, p.permission_description
            FROM {self.table} a
            JOIN schema_user.table_permission p ON p.permission_id = a.permission_id
            WHERE a.roles_id = %s AND a.deleted_at IS NULL AND p.deleted_at IS NULL
            ORDER BY p.permission_id
            """,
            (roles_id,),
        )

    def roles_with_permissions(self):
        return self.fetch_all(
            f"""
            SELECT a.roles_id, r.roles_description, p.permission_id, p.permission_description
            FROM {self.table} a
            JOIN schema_user.table_roles r ON r.roles_id = a.roles_id
            JOIN schema_user.table_permission p ON p.permission_id = a.permission_id
            WHERE a.deleted_at IS NULL AND r.deleted_at IS NULL AND p.deleted_at IS NULL
            ORDER BY a.roles_id, p.permission_id
            """
        )


class CategoryRepository(RepositoryBase):
    table = "schema_stock.table_category"

    def all_categories(self):
        return self.fetch_all(
            f"""
            SELECT category_id, category_description
            FROM {self.table}
            ORDER BY category_id
            """
        )


class SubcategoryRepository(RepositoryBase):
    table = "schema_stock.table_subcategory"

    def by_category(self, category_id):
        return self.fetch_all(
            f"""
            SELECT category_id, subcategory_id, subcategory_description
            FROM {self.table}
            WHERE category_id = %s
            ORDER BY subcategory_id
            """,
            (category_id,),
        )


class StockRepository(RepositoryBase):
    table = "schema_stock.table_stock"

    def catalog(self, query_text="", category_description="Semua"):
        query_text = f"%{query_text.strip()}%"
        parameters = []
        where_clauses = ["s.deleted_at IS NULL"]
        if query_text != "%%":
            where_clauses.append(
                "(s.stock_name LIKE %s OR s.stock_description LIKE %s OR c.category_description LIKE %s OR sub.subcategory_description LIKE %s)"
            )
            parameters.extend([query_text, query_text, query_text, query_text])
        if category_description not in (None, "", "Semua"):
            where_clauses.append("c.category_description = %s")
            parameters.append(category_description)

        query = f"""
            SELECT
                s.stock_id,
                s.stock_name,
                s.stock_subcategory,
                s.stock_rating,
                s.stock_description,
                s.stock_quantity,
                s.stock_price,
                c.category_id,
                c.category_description,
                sub.subcategory_id,
                sub.subcategory_description
            FROM {self.table} s
            JOIN (
                SELECT subcategory_id, MIN(category_id) AS category_id, MAX(subcategory_description) AS subcategory_description
                FROM schema_stock.table_subcategory
                GROUP BY subcategory_id
            ) sub ON sub.subcategory_id = s.stock_subcategory
            JOIN schema_stock.table_category c ON c.category_id = sub.category_id
            WHERE {' AND '.join(where_clauses)}
            ORDER BY s.stock_name
        """
        return self.fetch_all(query, tuple(parameters))

    def find_by_id(self, stock_id):
        return self.fetch_one(
            f"""
            SELECT
                s.stock_id,
                s.stock_name,
                s.stock_subcategory,
                s.stock_rating,
                s.stock_description,
                s.stock_quantity,
                s.stock_price,
                c.category_id,
                c.category_description,
                sub.subcategory_id,
                sub.subcategory_description
            FROM {self.table} s
            JOIN (
                SELECT subcategory_id, MIN(category_id) AS category_id, MAX(subcategory_description) AS subcategory_description
                FROM schema_stock.table_subcategory
                GROUP BY subcategory_id
            ) sub ON sub.subcategory_id = s.stock_subcategory
            JOIN schema_stock.table_category c ON c.category_id = sub.category_id
            WHERE s.stock_id = %s AND s.deleted_at IS NULL
            """,
            (stock_id,),
        )

    def categories(self):
        return self.fetch_all(
            """
            SELECT DISTINCT c.category_id, c.category_description
            FROM schema_stock.table_stock s
            JOIN (
                SELECT subcategory_id, MIN(category_id) AS category_id
                FROM schema_stock.table_subcategory
                GROUP BY subcategory_id
            ) sub ON sub.subcategory_id = s.stock_subcategory
            JOIN schema_stock.table_category c ON c.category_id = sub.category_id
            WHERE s.deleted_at IS NULL
            ORDER BY c.category_description
            """
        )

    def list_stock(self, limit=100):
        return self.fetch_all(
            f"""
            SELECT stock_id, stock_name, stock_subcategory, stock_rating, stock_quantity, stock_price, created_at
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY stock_id DESC
            LIMIT %s
            """,
            (limit,),
        )


class CartRepository(RepositoryBase):
    table = "schema_user.table_cart"

    def items_for_user(self, user_id):
        return self.fetch_all(
            f"""
            SELECT
                cart.cart_id,
                cart.user_id,
                cart.stock_id,
                cart.quantity,
                stock.stock_name,
                stock.stock_price,
                stock.stock_rating,
                stock.stock_quantity,
                stock.stock_description,
                c.category_description,
                sub.subcategory_description
            FROM {self.table} cart
            JOIN schema_stock.table_stock stock ON stock.stock_id = cart.stock_id
            JOIN (
                SELECT subcategory_id, MIN(category_id) AS category_id, MAX(subcategory_description) AS subcategory_description
                FROM schema_stock.table_subcategory
                GROUP BY subcategory_id
            ) sub ON sub.subcategory_id = stock.stock_subcategory
            JOIN schema_stock.table_category c ON c.category_id = sub.category_id
            WHERE cart.user_id = %s AND cart.deleted_at IS NULL AND stock.deleted_at IS NULL
            ORDER BY cart.created_at DESC, cart.cart_id DESC
            """,
            (user_id,),
        )

    def add_or_increment(self, user_id, stock_id, quantity=1, deleted_by=0):
        existing = self.fetch_one(
            f"""
            SELECT cart_id, quantity
            FROM {self.table}
            WHERE user_id = %s AND stock_id = %s AND deleted_at IS NULL
            """,
            (user_id, stock_id),
        )
        if existing:
            new_quantity = int(existing["quantity"]) + int(quantity)
            return self.execute(
                f"""
                UPDATE {self.table}
                SET quantity = %s, updated_at = NOW()
                WHERE cart_id = %s
                """,
                (new_quantity, existing["cart_id"]),
                commit=True,
            )

        return self.execute(
            f"""
            INSERT INTO {self.table}
                (user_id, stock_id, quantity, created_at, deleted_by)
            VALUES (%s, %s, %s, NOW(), %s)
            """,
            (user_id, stock_id, quantity, deleted_by),
            commit=True,
        )

    def change_quantity(self, user_id, stock_id, delta):
        existing = self.fetch_one(
            f"""
            SELECT cart_id, quantity
            FROM {self.table}
            WHERE user_id = %s AND stock_id = %s AND deleted_at IS NULL
            """,
            (user_id, stock_id),
        )
        if not existing:
            return 0

        new_quantity = int(existing["quantity"]) + int(delta)
        if new_quantity <= 0:
            return self.execute(
                f"DELETE FROM {self.table} WHERE cart_id = %s",
                (existing["cart_id"],),
                commit=True,
            )

        return self.execute(
            f"""
            UPDATE {self.table}
            SET quantity = %s, updated_at = NOW()
            WHERE cart_id = %s
            """,
            (new_quantity, existing["cart_id"]),
            commit=True,
        )

    def remove(self, user_id, stock_id):
        return self.execute(
            f"""
            DELETE FROM {self.table}
            WHERE user_id = %s AND stock_id = %s
            """,
            (user_id, stock_id),
            commit=True,
        )


class RatingRepository(RepositoryBase):
    table = "schema_user.table_rating"

    def ratings_for_stock(self, stock_id):
        return self.fetch_all(
            f"""
            SELECT rating_id, user_id, stock_id, rating, comment, created_at
            FROM {self.table}
            WHERE stock_id = %s AND deleted_at IS NULL
            ORDER BY created_at DESC
            """,
            (stock_id,),
        )


class ActivityRepository(RepositoryBase):
    table = "schema_utility.table_activity"

    def all_activity(self):
        return self.fetch_all(
            f"""
            SELECT activity_id, description, created_at
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY activity_id DESC
            """
        )


class LogRepository(RepositoryBase):
    table = "schema_utility.table_log"

    def logs_for_user(self, user_id):
        return self.fetch_all(
            f"""
            SELECT l.log_id, l.user_id, l.activity_id, a.description AS activity_description, l.created_at
            FROM {self.table} l
            LEFT JOIN schema_utility.table_activity a ON a.activity_id = l.activity_id
            WHERE l.user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )

    def latest_logs(self, limit=100):
        return self.fetch_all(
            f"""
            SELECT l.log_id, l.user_id, u.username, l.activity_id, a.description AS activity_description, l.created_at
            FROM {self.table} l
            LEFT JOIN schema_user.table_user u ON u.user_id = l.user_id
            LEFT JOIN schema_utility.table_activity a ON a.activity_id = l.activity_id
            ORDER BY l.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )


class BlacklistReasonRepository(RepositoryBase):
    table = "schema_utility.table_blacklist_reason"

    def all_reasons(self):
        return self.fetch_all(
            f"""
            SELECT cause_id, reason
            FROM {self.table}
            WHERE deleted_at IS NULL
            ORDER BY cause_id
            """
        )


class BlacklistRepository(RepositoryBase):
    table = "schema_utility.table_blacklist"

    def all_blacklisted_users(self):
        return self.fetch_all(
            f"""
            SELECT b.user_id, u.username, b.cause_id, r.reason, b.created_at
            FROM {self.table} b
            JOIN schema_user.table_user u ON u.user_id = b.user_id
            JOIN schema_utility.table_blacklist_reason r ON r.cause_id = b.cause_id
            WHERE b.deleted_at IS NULL AND u.deleted_at IS NULL AND r.deleted_at IS NULL
            ORDER BY b.created_at DESC
            """
        )