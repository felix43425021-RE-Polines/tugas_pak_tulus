from abc import abstractmethod
from importlib import import_module
from dotenv import dotenv_values, load_dotenv
import tkinter as tk
from tkinter import ttk

from .PresenterFactory import PresenterFactory

class Router(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dotenv_path = ".env"
        load_dotenv(dotenv_path)
        env = dotenv_values(dotenv_path)
        self.title(env.get("APP_NAME", "MVP App"))
        self.geometry(env.get("APP_GEOMETRY", "600x400"))
        self.state(env.get("APP_STATE", "normal"))
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.pages = {}
        self.presenters = {}
        self.current_page_name = None
        self.presenter_factory = PresenterFactory()
        self.shared_model = self._create_shared_model()

        for route_name, route_config in self.routes.items():
            view_class = self._resolve_class(route_config["view"])
            presenter_ref = route_config.get("presenter")
            presenter_class = self._resolve_class(presenter_ref) if presenter_ref else None

            page_instance = view_class(parent=container, router=self)
            self.pages[route_name] = page_instance

            presenter = self.presenter_factory.create(
                presenter_class,
                view=page_instance,
                router=self,
                model=self.shared_model,
            )
            if presenter is not None:
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
        current_presenter = self.presenters.get(self.current_page_name)
        if current_presenter is not None:
            current_presenter.stop()

        page = self.pages.get(page_name)
        if page:
            page.tkraise()
            self.current_page_name = page_name

            current_presenter = self.presenters.get(page_name)
            if current_presenter is not None:
                current_presenter.start()
        else:
            print(f"Error: Page '{page_name}' does not exist.")

    def get_presenter(self, page_name):
        return self.presenters.get(page_name)

    def _create_shared_model(self):
        model_ref = getattr(self, "app_model", None)
        if not model_ref:
            return None

        model_class = self._resolve_class(model_ref)
        return model_class()

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
