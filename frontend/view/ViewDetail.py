from tkinter import ttk

from .BaseView import BaseView


class ViewDetail(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")
        ttk.Button(top, text="Kembali ke Beranda", command=self.back_home).pack(anchor="w")

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        self.image_box = ttk.Frame(body, width=240, height=240, relief="ridge")
        self.image_box.pack(side="left", padx=(0, 16))
        self.image_box.pack_propagate(False)
        ttk.Label(self.image_box, text="Preview Produk").pack(expand=True)

        info = ttk.Frame(body)
        info.pack(side="left", fill="both", expand=True)

        self.name_label = ttk.Label(info, text="", font=("Arial", 18, "bold"), wraplength=320)
        self.name_label.pack(anchor="w")
        self.price_label = ttk.Label(info, text="", font=("Arial", 12, "bold"))
        self.price_label.pack(anchor="w", pady=(8, 0))
        self.meta_label = ttk.Label(info, text="")
        self.meta_label.pack(anchor="w", pady=(8, 0))
        self.description_label = ttk.Label(info, text="", wraplength=340, justify="left")
        self.description_label.pack(anchor="w", pady=(12, 0))
        self.message_label = ttk.Label(info, text="")
        self.message_label.pack(anchor="w", pady=(12, 0))

        button_row = ttk.Frame(info)
        button_row.pack(anchor="w", pady=(16, 0))
        ttk.Button(button_row, text="Tambah ke Keranjang", command=self.add_to_cart).pack(side="left")
        ttk.Button(button_row, text="Beli Sekarang", command=self.buy_now).pack(side="left", padx=8)

    def render_product(self, product):
        self.name_label.config(text=product["name"])
        self.price_label.config(text=self.format_currency(product["price"]))
        self.meta_label.config(text=f"Kategori: {product['category']} | Stok: {product['stock']} | Rating: {product['rating']}")
        self.description_label.config(text=product["description"])
        self.message_label.config(text="")

    def show_message(self, message):
        self.message_label.config(text=message)

    def add_to_cart(self):
        if self.presenter is not None:
            self.presenter.add_to_cart()

    def buy_now(self):
        if self.presenter is not None:
            self.presenter.buy_now()

    def back_home(self):
        if self.presenter is not None:
            self.presenter.back_home()
        else:
            self.open_route("Home")
