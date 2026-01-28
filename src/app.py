from fastapi import FastAPI
from src.routes import conversation_router, user_router

app = FastAPI()
app.include_router(conversation_router)
app.include_router(user_router)
