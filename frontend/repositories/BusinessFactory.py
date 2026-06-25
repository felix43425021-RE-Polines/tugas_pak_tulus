from repositories.BusinessRepositories import (
    ActivityRepository,
    AuthorizationRepository,
    BlacklistReasonRepository,
    BlacklistRepository,
    CartRepository,
    CategoryRepository,
    LogRepository,
    PermissionRepository,
    RatingRepository,
    RoleRepository,
    StockRepository,
    SubcategoryRepository,
    UserRepository,
)


class BusinessFactory:
    def __init__(self, database=None):
        self.database = database

    def user(self):
        return UserRepository(self.database)

    def stock(self):
        return StockRepository(self.database)

    def authorization(self):
        return AuthorizationRepository(self.database)

    def permission(self):
        return PermissionRepository(self.database)

    def role(self):
        return RoleRepository(self.database)

    def cart(self):
        return CartRepository(self.database)

    def rating(self):
        return RatingRepository(self.database)

    def category(self):
        return CategoryRepository(self.database)

    def subcategory(self):
        return SubcategoryRepository(self.database)

    def activity(self):
        return ActivityRepository(self.database)

    def log(self):
        return LogRepository(self.database)

    def blacklist_reason(self):
        return BlacklistReasonRepository(self.database)

    def blacklist(self):
        return BlacklistRepository(self.database)
