import tkinter as tk
from tkinter import ttk
from BaseView import BaseView


class ViewHome(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent)

        label = ttk.Label(self, text="Welcome to the Home Page", font=("Arial", 18))
        label.pack(pady=20)

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=8)

        btn_settings = ttk.Button(self, text="Go to Settings", command=self.go_settings)
        btn_settings.pack(pady=10)

        btn_profile = ttk.Button(self, text="Go to Profile", command=self.go_profile)
        btn_profile.pack(pady=10)

    def go_settings(self):
        if self.presenter is not None:
            self.presenter.open_settings()
        else:
            self.open_route("Settings")

    def go_profile(self):
        if self.presenter is not None:
            self.presenter.open_profile()
        else:
            self.open_route("Profile")