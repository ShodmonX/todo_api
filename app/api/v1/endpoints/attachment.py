from fastapi import APIRouter


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"]
)

@router.get("/")
async def get_attachments():
    return {"status": "ok"}