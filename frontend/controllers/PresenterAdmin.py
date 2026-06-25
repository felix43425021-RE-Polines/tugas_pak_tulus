from .Presenter import Presenter


class PresenterAdmin(Presenter):
    def __init__(self, view=None, router=None, model=None):
        super().__init__(view=view, router=router, model=model)

    def start(self):
        self.refresh()

    def refresh(self):
        if not self.model.can_access_admin():
            self.present("set_notice", "Akses Admin ditolak.")
            self.navigate("Home")
            return

        snapshot = self.model.admin_snapshot(limit=100)
        self.present("render_snapshot", snapshot)

    def back_home(self):
        self.navigate("Home")
