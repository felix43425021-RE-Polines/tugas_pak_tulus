from .Presenter import Presenter


class PresenterProfile(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)

    def start(self):
        self.present("render_profile", self.model.user, len(self.model.cart_items()))

    def back_home(self):
        self.navigate("Home")

    def logout(self):
        self.model.logout()
        self.navigate("Login")

    def open_admin(self):
        if self.model.can_access_admin():
            self.navigate("Admin")
