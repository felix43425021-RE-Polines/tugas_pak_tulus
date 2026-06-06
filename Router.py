from abc import abstractmethod
from importlib import import_module
import tkinter as tk
from tkinter import ttk

class Router(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.title("Multipage Tkinter Application")
        self.geometry("600x400")
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.pages = {}
        self.presenters = {}

        for route_name, route_config in self.routes.items():
            view_class = self._resolve_class(route_config["view"])
            presenter_ref = route_config.get("presenter")
            presenter_class = self._resolve_class(presenter_ref) if presenter_ref else None

            page_instance = view_class(parent=container, router=self)
            self.pages[route_name] = page_instance

            if presenter_class is not None:
                presenter = presenter_class(view=page_instance, router=self)
                self.presenters[route_name] = presenter
                if hasattr(page_instance, "attach_presenter"):
                    page_instance.attach_presenter(presenter)
            
            # Put all pages in the exact same grid location
            page_instance.grid(row=0, column=0, sticky="nsew")
            
        # Start the application by showing the Home Page
        first_route_name = next(iter(self.routes))
        self.show_page(first_route_name)

    def show_page(self, page_name):
        """ Brings the specified page frame to the front. """
        page = self.pages.get(page_name)
        if page:
            page.tkraise()
        else:
            print(f"Error: Page '{page_name}' does not exist.")

    def _resolve_class(self, class_ref):
        if isinstance(class_ref, str):
            module_name, class_name = class_ref.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, class_name)
        return class_ref

    
    @property
    @abstractmethod
    def routes(self):
        pass