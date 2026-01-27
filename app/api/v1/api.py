from fastapi import APIRouter

from .auth import router as auth_router
from .task import router as task_router
from .user import router as user_router
from .category import router as category_router
from .attachment import router as attachment_router
from .subtask import router as subtask_router


router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(task_router)
router.include_router(user_router)
router.include_router(category_router)
router.include_router(attachment_router)
router.include_router(subtask_router)
