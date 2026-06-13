from Presenter import Presenter
from ModelItem import ModelItem

class PresenterHome(Presenter):
    def __init__(self, view=None, router=None):
        super().__init__(view=view, router=router, model=ModelItem())

    def open_settings(self):
        self.navigate("Settings")

    def open_profile(self):
        self.navigate("Profile")

    def start(self):
        self.load_item_summary()

    def stop(self):
        self.present("set_status", "")

    def load_item_summary(self):
        try:
            items = self.model.ReadAll()
            item_count = len(items)
            self.present("set_status", f"Total item: {item_count}")
            return item_count
        except Exception as exc:
            self.present("set_status", f"Model belum siap: {exc.__class__.__name__}")
            return None

    