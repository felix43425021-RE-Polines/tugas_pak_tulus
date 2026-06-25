from .Presenter import Presenter


class PresenterCart(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)

    def start(self):
        self.refresh_cart()

    def refresh_cart(self):
        self.present("render_cart", self.model.cart_items(), self.model.cart_total())

    def increase_qty(self, product_id):
        self.model.change_cart_quantity(product_id, 1)
        self.refresh_cart()

    def decrease_qty(self, product_id):
        self.model.change_cart_quantity(product_id, -1)
        self.refresh_cart()

    def remove_item(self, product_id):
        self.model.remove_from_cart(product_id)
        self.refresh_cart()

    def checkout(self):
        self.present("show_message", "Pembayaran sederhana belum dihubungkan.")

    def back_home(self):
        self.navigate("Home")
