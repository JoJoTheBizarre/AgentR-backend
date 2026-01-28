from fastapi import APIRouter


conversation_router = APIRouter(prefix="/conversation")


@conversation_router.get("/")
def top():
    return "top level conversations route"