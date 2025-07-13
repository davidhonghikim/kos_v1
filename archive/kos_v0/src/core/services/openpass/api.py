from fastapi import APIRouter

router = APIRouter()

@router.get("/openpass")
def get_passphrase():
    return {"passphrase": "correct-horse-battery-staple"}
