from dotenv import dotenv_values, load_dotenv
import mysql.connector


class Database:
  def __init__(self):
    load_dotenv()
    self.env = dotenv_values(".env")
    self.db = None
    self.cursor = None
    self.connected = False

    try:
      self.db = mysql.connector.connect(
        host=self.env.get("DB_HOST"),
        user=self.env.get("DB_USERNAME"),
        password=self.env.get("DB_PASSWORD"),
        database=self.env.get("DB_NAME"),
      )
      self.cursor = self.db.cursor(dictionary=True)
      self.connected = True
    except Exception:
      self.db = None
      self.cursor = None
      self.connected = False

  def close(self):
    if self.cursor is not None:
      self.cursor.close()
    if self.db is not None:
      self.db.close()