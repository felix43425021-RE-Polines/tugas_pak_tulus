from tkinter import ttk

from .BaseView import BaseView


class ViewSettings(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)
        
        label = ttk.Label(self, text="Settings Menu", font=("Arial", 18))
        label.pack(pady=20)
        
        # Checkbox placeholder for demonstration
        chk = ttk.Checkbutton(self, text="Enable Notifications")
        chk.pack(pady=10)
        
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
