from .Presenter import Presenter


class PresenterDetail(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)

    def start(self):
        product = self.model.selected_product()
        if product is None:
            self.navigate("Home")
            return
        self.present("render_product", product)

    def add_to_cart(self):
        product = self.model.selected_product()
        if product is None:
            self.navigate("Home")
            return
        self.model.add_to_cart(product["id"])
        self.present("show_message", f"{product['name']} ditambahkan ke keranjang.")

    def buy_now(self):
        product = self.model.selected_product()
        if product is None:
            self.navigate("Home")
            return
        self.model.add_to_cart(product["id"])
        self.navigate("Cart")

    def back_home(self):
        self.navigate("Home")
