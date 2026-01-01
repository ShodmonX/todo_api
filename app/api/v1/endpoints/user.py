from fastapi import APIRouter, Depends

from typing import Annotated, Any

from app.dependencies import get_current_user
from app.schemas import UserOut


router = APIRouter(
    prefix="/user",
    tags=["User"]
)

@router.get("/me", response_model=UserOut)
async def get_me(user: Annotated[dict[str, Any], Depends(get_current_user)]):
    return user