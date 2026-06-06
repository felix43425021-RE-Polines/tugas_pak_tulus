import mysql.connector
from dotenv import *

class Database:
    def __init__(self):
        load_dotenv()
        self.env = dotenv_values(".env")
        self.db = mysql.connector.connect(
          host=self.env["DB_HOST"],
          user=self.env["DB_USERNAME"],
          password=self.env["DB_PASSWORD"],
          database=self.env["DB_NAME"]
        )
        self.cursor = self.db.cursor()