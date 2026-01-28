from fastapi import APIRouter


conversation_router = APIRouter(prefix="/conversation")


@conversation_router.get("/")
def get_conversations():
    """Placeholder endpoint for conversation listing."""
    return "top level conversations route"
