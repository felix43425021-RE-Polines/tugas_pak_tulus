import os
import sys

from fastapi import FastAPI

sys.path.insert(0, os.path.dirname(__file__))

from apis import stock_router, user_router, utility_router
from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Multi-Schema E-Commerce API",
    description="API menggunakan FastAPI, SQLAlchemy 2.0, dan database dengan 3 skema berbeda.",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(stock_router)
app.include_router(utility_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "API berjalan."}
