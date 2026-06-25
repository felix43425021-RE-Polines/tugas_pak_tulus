from dotenv import dotenv_values, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
config = dotenv_values(".env")
engine = create_engine(f"mysql+pymysql://{config['DB_USERNAME']}:{config['DB_PASSWORD']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}", echo=True)
local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()