import tkinter as tk
from tkinter import ttk


class Router(tk.Tk):
    """ The main application controller (Router) that manages and switches pages. """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Multipage Tkinter Application")
        self.geometry("600x400")
        
        # Create a central container that fills the window
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to store references to initialized page objects
        self.pages = {}
        
        # Define the pages in the application
        page_classes = (HomePage, SettingsPage, ProfilePage)
        
        # Initialize each page and stack them in the container grid
        for PageClass in page_classes:
            page_name = PageClass.__name__
            page_instance = PageClass(parent=container, router=self)
            self.pages[page_name] = page_instance
            
            # Put all pages in the exact same grid location
            page_instance.grid(row=0, column=0, sticky="nsew")
            
        # Start the application by showing the Home Page
        self.show_page("HomePage")

    def show_page(self, page_name):
        """ Brings the specified page frame to the front. """
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
        else:
            print(f"Error: Page '{page_name}' does not exist.")


class HomePage(ttk.Frame):
    """ The application home page. """
    
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router
        
        # Page Title
        label = ttk.Label(self, text="Welcome to the Home Page", font=("Arial", 18))
        label.pack(pady=20)
        
        # Navigation Buttons
        btn_settings = ttk.Button(
            self, 
            text="Go to Settings", 
            command=lambda: router.show_page("SettingsPage")
        )
        btn_settings.pack(pady=10)
        
        btn_profile = ttk.Button(
            self, 
            text="Go to Profile", 
            command=lambda: router.show_page("ProfilePage")
        )
        btn_profile.pack(pady=10)


class SettingsPage(ttk.Frame):
    """ The application settings page. """
    
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
            command=lambda: router.show_page("HomePage")
        )
        btn_home.pack(pady=10)


class ProfilePage(ttk.Frame):
    """ The application user profile page. """
    
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router
        
        label = ttk.Label(self, text="User Profile", font=("Arial", 18))
        label.pack(pady=20)
        
        lbl_info = ttk.Label(self, text="Username: JohnDoe\nStatus: Active")
        lbl_info.pack(pady=10)
        
        btn_home = ttk.Button(
            self, 
            text="Back to Home", 
            command=lambda: router.show_page("HomePage")
        )
        btn_home.pack(pady=10)


if __name__ == "__main__":
    app = Router()
    app.mainloop()
