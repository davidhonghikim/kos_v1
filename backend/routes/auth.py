"""
Authentication Routes

Basic authentication endpoints for the Amauta system.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Basic login endpoint"""
    # TODO: Implement actual authentication
    if request.username == "admin" and request.password == "password":
        return LoginResponse(access_token="dummy_token")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
async def get_current_user():
    """Get current user information"""
    return {"username": "admin", "role": "admin"}
