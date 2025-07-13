from fastapi import APIRouter

router = APIRouter()

@router.get("/prompts")
def list_prompts():
    return {"prompts": ["greet", "summarize"]}
