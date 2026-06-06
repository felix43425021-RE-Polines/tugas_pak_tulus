from abc import abstractmethod
from Database import Database

class Model(Database):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def table(self):
        pass

    @property
    @abstractmethod
    def allowed_fields(self):
        pass

    def Insert(self, data_table: dict):
        filtered_data = {k: v for k, v in data_table.items() if k in self.allowed_fields}
        keys_str = ", ".join(filtered_data.keys())
        values_str = ", ".join([f"'{value}'" for value in filtered_data.values()])
        self.cursor.execute(f"INSERT INTO {self.table} ({keys_str}) VALUES ({values_str})")
        self.db.commit()

    def Delete(self, primary_key):
        self.cursor.execute(f"DELETE FROM {self.table} WHERE id = {primary_key}")
        self.db.commit()


