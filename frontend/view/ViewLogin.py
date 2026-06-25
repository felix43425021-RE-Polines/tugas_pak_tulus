from tkinter import ttk

from .BaseView import BaseView


class ViewLogin(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        wrapper = ttk.Frame(self, padding=24)
        wrapper.pack(expand=True)

        card = ttk.Frame(wrapper, padding=24, relief="ridge")
        card.pack()

        ttk.Label(card, text="Tokokita - Login", font=("Arial", 18, "bold")).pack(pady=(0, 16))
        ttk.Label(card, text="Email address").pack(anchor="w")
        self.email_entry = ttk.Entry(card, width=32)
        self.email_entry.pack(pady=(4, 12))

        ttk.Label(card, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(card, width=32, show="*")
        self.password_entry.pack(pady=(4, 12))

        ttk.Button(card, text="Masuk", command=self.login).pack(fill="x", pady=(4, 8))
        self.message_label = ttk.Label(card, text="")
        self.message_label.pack(pady=(4, 0))

    def reset_form(self):
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.message_label.config(text="")

    def show_message(self, message, success=False):
        self.message_label.config(text=message)

    def login(self):
        if self.presenter is not None:
            self.presenter.login(self.email_entry.get(), self.password_entry.get())
