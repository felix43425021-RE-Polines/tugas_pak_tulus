from .Presenter import Presenter

class PresenterLogin(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)

    def start(self):
        self.present("reset_form")

    def login(self, username, password):
        success, message = self.model.authenticate(username, password)
        self.present("show_message", message, success)
        if success:
            self.navigate("Home")
