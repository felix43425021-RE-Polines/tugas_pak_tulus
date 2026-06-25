from tkinter import ttk

from .BaseView import BaseView


class ViewCart(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="Keranjang Belanja Anda", font=("Arial", 18, "bold")).pack(side="left")
        ttk.Button(top, text="Kembali ke Beranda", command=self.back_home).pack(side="right")

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.pack(fill="both", expand=True)

        self.items_frame = ttk.Frame(body)
        self.items_frame.pack(side="left", fill="both", expand=True)

        self.summary_frame = ttk.Frame(body, padding=16, relief="ridge")
        self.summary_frame.pack(side="right", fill="y", padx=(16, 0))

        ttk.Label(self.summary_frame, text="Ringkasan Pesanan", font=("Arial", 14, "bold")).pack(anchor="w")
        self.subtotal_label = ttk.Label(self.summary_frame, text="Subtotal: -")
        self.subtotal_label.pack(anchor="w", pady=(12, 0))
        self.shipping_label = ttk.Label(self.summary_frame, text="Shipping: JNE Regular")
        self.shipping_label.pack(anchor="w", pady=(4, 0))
        self.total_label = ttk.Label(self.summary_frame, text="Total Price: -", font=("Arial", 12, "bold"))
        self.total_label.pack(anchor="w", pady=(8, 0))
        ttk.Button(self.summary_frame, text="Lanjutkan ke Pembayaran", command=self.checkout).pack(fill="x", pady=(16, 0))
        self.message_label = ttk.Label(self.summary_frame, text="")
        self.message_label.pack(anchor="w", pady=(12, 0))

    def render_cart(self, items, total):
        self.clear_children(self.items_frame)
        if not items:
            ttk.Label(self.items_frame, text="Keranjang masih kosong.").pack(anchor="w", pady=12)
            self.subtotal_label.config(text="Subtotal: -")
            self.total_label.config(text="Total Price: -")
            return

        for item in items:
            product = item["product"]
            row = ttk.Frame(self.items_frame, padding=12, relief="ridge")
            row.pack(fill="x", pady=6)

            left = ttk.Frame(row)
            left.pack(side="left", fill="x", expand=True)
            ttk.Label(left, text=product["name"], font=("Arial", 11, "bold")).pack(anchor="w")
            ttk.Label(left, text=self.format_currency(product["price"])).pack(anchor="w")

            middle = ttk.Frame(row)
            middle.pack(side="left", padx=16)
            ttk.Button(middle, text="-", width=3, command=lambda value=product["id"]: self.decrease_qty(value)).pack(side="left")
            ttk.Label(middle, text=str(item["quantity"]), width=4, anchor="center").pack(side="left")
            ttk.Button(middle, text="+", width=3, command=lambda value=product["id"]: self.increase_qty(value)).pack(side="left")

            right = ttk.Frame(row)
            right.pack(side="right")
            ttk.Label(right, text=self.format_currency(item["subtotal"]), font=("Arial", 10, "bold")).pack(anchor="e")
            ttk.Button(right, text="Hapus", command=lambda value=product["id"]: self.remove_item(value)).pack(anchor="e", pady=(6, 0))

        self.subtotal_label.config(text=f"Subtotal: {self.format_currency(total)}")
        self.total_label.config(text=f"Total Price: {self.format_currency(total)}")

    def show_message(self, message):
        self.message_label.config(text=message)

    def increase_qty(self, product_id):
        if self.presenter is not None:
            self.presenter.increase_qty(product_id)

    def decrease_qty(self, product_id):
        if self.presenter is not None:
            self.presenter.decrease_qty(product_id)

    def remove_item(self, product_id):
        if self.presenter is not None:
            self.presenter.remove_item(product_id)

    def checkout(self):
        if self.presenter is not None:
            self.presenter.checkout()

    def back_home(self):
        if self.presenter is not None:
            self.presenter.back_home()
        else:
            self.open_route("Home")
