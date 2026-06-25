from .Migration import Migration

class MigrationItem(Migration):
    def __init__(self):
        super().__init__()

    def CreateItemTable(self):
        columns = {
            "id": "INTEGER PRIMARY KEY AUTO_INCREMENT",
            "name": "TEXT NOT NULL",
            "description": "TEXT",
            "price": "REAL NOT NULL",
            "quantity": "INTEGER NOT NULL"
        }
        self.CreateTable("items", columns)

    def DropItemTable(self):
        self.DropTable("items")

migration_item = MigrationItem()
migration_item.DropItemTable()
