from tkinter import ttk
from .BaseView import BaseView


class ViewHome(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        header = ttk.Frame(self, padding=16)
        header.pack(fill="x")

        left = ttk.Frame(header)
        left.pack(side="left")
        ttk.Label(left, text="Tokokita", font=("Arial", 20, "bold")).pack(anchor="w")
        ttk.Label(left, text="Cari produk terbaik untuk kebutuhan harian").pack(anchor="w")

        right = ttk.Frame(header)
        right.pack(side="right", fill="x", expand=True)
        self.search_entry = ttk.Entry(right)
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda event: self.search_products())
        ttk.Button(right, text="Cari", command=self.search_products).pack(side="left", padx=(8, 0))

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.pack(fill="both", expand=True)

        sidebar = ttk.Frame(body, width=140)
        sidebar.pack(side="left", fill="y")
        ttk.Button(sidebar, text="Beranda", command=self.go_home).pack(fill="x", pady=(0, 8))
        ttk.Button(sidebar, text="Keranjang", command=self.go_cart).pack(fill="x", pady=8)
        ttk.Button(sidebar, text="Profil", command=self.go_profile).pack(fill="x", pady=8)
        ttk.Button(sidebar, text="Admin", command=self.go_admin).pack(fill="x", pady=8)
        ttk.Button(sidebar, text="Logout", command=self.logout).pack(fill="x", pady=8)

        content = ttk.Frame(body)
        content.pack(side="left", fill="both", expand=True, padx=(16, 0))

        self.status_label = ttk.Label(content, text="")
        self.status_label.pack(anchor="w", pady=(0, 10))

        ttk.Label(content, text="Kategori").pack(anchor="w")
        self.category_frame = ttk.Frame(content)
        self.category_frame.pack(fill="x", pady=(4, 10))

        ttk.Label(content, text="Produk").pack(anchor="w")
        self.products_frame = ttk.Frame(content)
        self.products_frame.pack(fill="both", expand=True, pady=(8, 0))

    def search_products(self):
        if self.presenter is not None:
            self.presenter.search(self.search_entry.get())

    def go_home(self):
        if self.presenter is not None:
            self.presenter.filter_category("Semua")
        else:
            self.open_route("Home")

    def go_cart(self):
        if self.presenter is not None:
            self.presenter.open_cart()
        else:
            self.open_route("Cart")

    def go_profile(self):
        if self.presenter is not None:
            self.presenter.open_profile()
        else:
            self.open_route("Profile")

    def go_admin(self):
        if self.presenter is not None:
            self.presenter.open_admin()
        else:
            self.open_route("Admin")

    def logout(self):
        if self.presenter is not None:
            self.presenter.logout()
        else:
            self.open_route("Login")

    def render_categories(self, categories, active_category):
        self.clear_children(self.category_frame)
        for category in categories:
            ttk.Button(
                self.category_frame,
                text=category,
                command=lambda value=category: self.presenter.filter_category(value) if self.presenter else None,
            ).pack(side="left", padx=(0, 8), pady=4)

    def render_products(self, products):
        self.clear_children(self.products_frame)
        if not products:
            ttk.Label(self.products_frame, text="Produk tidak ditemukan.").pack(anchor="w", pady=12)
            return

        for index, product in enumerate(products):
            card = ttk.Frame(self.products_frame, padding=12, relief="ridge")
            card.grid(row=index // 3, column=index % 3, padx=8, pady=8, sticky="nsew")
            self.products_frame.grid_columnconfigure(index % 3, weight=1)

            preview = ttk.Frame(card, width=120, height=90)
            preview.pack(fill="x")
            preview.pack_propagate(False)
            ttk.Label(preview, text=product["category"], anchor="center").pack(expand=True)

            ttk.Label(card, text=product["name"], wraplength=180, justify="left").pack(anchor="w", pady=(10, 2))
            ttk.Label(card, text=self.format_currency(product["price"]), font=("Arial", 10, "bold")).pack(anchor="w")
            ttk.Button(
                card,
                text="Lihat Detail",
                command=lambda value=product["id"]: self.presenter.open_product(value) if self.presenter else None,
            ).pack(anchor="e", pady=(10, 0))
