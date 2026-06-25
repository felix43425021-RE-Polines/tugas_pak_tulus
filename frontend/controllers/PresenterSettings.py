from .Presenter import Presenter


class PresenterSettings(Presenter):
    def __init__(self, view=None, router=None):
        super().__init__(view=view, router=router)

    def back_home(self):
        self.view("Home")
