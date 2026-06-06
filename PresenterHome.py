from Presenter import Presenter
from ModelItem import ModelItem

class PresenterHome(Presenter):
    def __init__(self, view=None, router=None):
        super().__init__(view=view, router=router, model=ModelItem())

    def open_settings(self):
        self.view("Settings")

    def open_profile(self):
        self.view("Profile")

    