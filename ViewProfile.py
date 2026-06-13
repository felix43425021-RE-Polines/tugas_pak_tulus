from tkinter import ttk

from BaseView import BaseView


class ViewProfile(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        label = ttk.Label(self, text="Profile Menu", font=("Arial", 18))
        label.pack(pady=20)
        btn_home = ttk.Button(
            self,
            text="Back to Home",
            command=self.go_home
        )
        btn_home.pack(pady=10)

    def go_home(self):
        if self.presenter is not None:
            self.presenter.back_home()
        else:
            self.open_route("Home")