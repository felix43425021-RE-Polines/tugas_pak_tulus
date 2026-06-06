
from tkinter import ttk

class ViewProfile(ttk.Frame):
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router

        label = ttk.Label(self, text="Profile Menu", font=("Arial", 18))
        label.pack(pady=20)
        btn_home = ttk.Button(
            self,
            text="Back to Home",
            command=lambda: router.show_page("Home")
        )
        btn_home.pack(pady=10)