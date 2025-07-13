from fastapi import APIRouter

router = APIRouter()

@router.get("/vault")
def vault_status():
    return {"status": "vault ok"}
