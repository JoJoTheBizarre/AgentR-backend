from fastapi import FastAPI
from src.routes import user_router
from src.db import init_database
from src.settings import DatabaseSettings

#setup db manager and engine
db_settings = DatabaseSettings() #type: ignore
init_database(db_settings.DATABASE_URL)

app = FastAPI()
app.include_router(user_router)
