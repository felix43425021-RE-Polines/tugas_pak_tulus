from Model import Model

class ModelItem(Model):
    @property
    def table(self):
        return "items"
    
    @property
    def allowed_fields(self):
        return ["id", "name", "price", "stock"]