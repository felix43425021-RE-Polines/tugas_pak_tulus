import tkinter as tk
from tkinter import ttk


class ViewHome(ttk.Frame):
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router
        self.presenter = None

        label = ttk.Label(self, text="Welcome to the Home Page", font=("Arial", 18))
        label.pack(pady=20)

        btn_settings = ttk.Button(self, text="Go to Settings", command=self.go_settings)
        btn_settings.pack(pady=10)

        btn_profile = ttk.Button(self, text="Go to Profile", command=self.go_profile)
        btn_profile.pack(pady=10)

    def attach_presenter(self, presenter):
        self.presenter = presenter

    def go_settings(self):
        if self.presenter is not None:
            self.presenter.open_settings()
        else:
            self.router.show_page("Settings")

    def go_profile(self):
        if self.presenter is not None:
            self.presenter.open_profile()
        else:
            self.router.show_page("Profile")