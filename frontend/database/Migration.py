from .Database import Database

class Migration(Database):
    def __init__(self):
        super().__init__()

    def CreateTable(self, table_name, columns: dict):
        columns_str = ", ".join([f"{column} {constraint}" for column, constraint in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.cursor.execute(sql)
        self.db.commit()

    def DropTable(self, table_name):
        sql = f"DROP TABLE IF EXISTS {table_name}"
        self.cursor.execute(sql)
        self.db.commit()
    
