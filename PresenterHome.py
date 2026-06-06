from Presenter import Presenter
from ModelItem import ModelItem

class PresenterHome(Presenter):
    def __init__(self):
        super().__init__()
        self.ModelItem = ModelItem()

    