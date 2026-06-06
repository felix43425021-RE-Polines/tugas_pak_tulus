
from tkinter import ttk
class ViewSettings (ttk.Frame):
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router
        
        label = ttk.Label(self, text="Settings Menu", font=("Arial", 18))
        label.pack(pady=20)
        
        # Checkbox placeholder for demonstration
        chk = ttk.Checkbutton(self, text="Enable Notifications")
        chk.pack(pady=10)
        
        btn_home = ttk.Button(
            self, 
            text="Back to Home", 
            command=lambda: router.show_page("Home")
        )
        btn_home.pack(pady=10)