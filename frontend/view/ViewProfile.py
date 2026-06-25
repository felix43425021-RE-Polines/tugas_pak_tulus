from tkinter import ttk

from .BaseView import BaseView


class ViewProfile(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="Profil Pengguna", font=("Arial", 18, "bold")).pack(side="left")
        ttk.Button(top, text="Kembali ke Beranda", command=self.go_home).pack(side="right")

        body = ttk.Frame(self, padding=16)
        body.pack(fill="both", expand=True)

        self.name_label = ttk.Label(body, text="Nama: -", font=("Arial", 12))
        self.name_label.pack(anchor="w", pady=(0, 8))
        self.email_label = ttk.Label(body, text="Email: -")
        self.email_label.pack(anchor="w", pady=(0, 8))
        self.cart_label = ttk.Label(body, text="Item di keranjang: 0")
        self.cart_label.pack(anchor="w", pady=(0, 8))

        ttk.Button(body, text="Buka Admin", command=self.open_admin).pack(anchor="w", pady=(0, 8))
        ttk.Button(body, text="Logout", command=self.logout).pack(anchor="w", pady=(16, 0))

    def render_profile(self, user, cart_count):
        self.name_label.config(text=f"Nama: {user['name']}")
        self.email_label.config(text=f"Email: {user['email'] or '-'}")
        self.cart_label.config(text=f"Item di keranjang: {cart_count}")

    def go_home(self):
        if self.presenter is not None:
            self.presenter.back_home()
        else:
            self.open_route("Home")

    def logout(self):
        if self.presenter is not None:
            self.presenter.logout()
        else:
            self.open_route("Login")

    def open_admin(self):
        if self.presenter is not None:
            self.presenter.open_admin()
        else:
            self.open_route("Admin")
