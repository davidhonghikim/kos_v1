from fastapi import APIRouter

router = APIRouter()

@router.get("/artifacts")
def list_artifacts():
    return {"artifacts": ["image.png", "audio.wav"]}
