from .Presenter import Presenter


class PresenterHome(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)
        self.current_category = "Semua"
        self.current_query = ""

    def start(self):
        self.refresh_home()

    def stop(self):
        self.present("set_status", "")

    def refresh_home(self):
        categories = self.model.categories()
        products = self.model.search_products(self.current_query, self.current_category)
        self.present("render_categories", categories, self.current_category)
        self.present("render_products", products)
        self.present("set_status", f"Halo, {self.model.user['name']}")

    def search(self, query):
        self.current_query = query
        self.refresh_home()

    def filter_category(self, category):
        self.current_category = category
        self.refresh_home()

    def open_product(self, product_id):
        self.model.select_product(product_id)
        self.navigate("Detail")

    def open_cart(self):
        self.navigate("Cart")

    def open_profile(self):
        self.navigate("Profile")

    def open_admin(self):
        if self.model.can_access_admin():
            self.navigate("Admin")
            return
        self.present("set_status", "Akses Admin ditolak")

    def logout(self):
        self.model.logout()
        self.navigate("Login")

    
