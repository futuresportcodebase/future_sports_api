from fastapi import APIRouter, Query
import os
from .endpoints import items, users, web3, images

router = APIRouter()


@router.get("")
async def root():
    return {
        "ENV": os.getenv("ENV", default="dev"),
        "message": "Hello World!",
        "SOME_ENV": os.getenv("SOME_ENV", default=""),
        "OTHER_ENV": os.getenv("OTHER_ENV", default=""),
    }


router.include_router(items.router)
router.include_router(users.router)
router.include_router(web3.router)
router.include_router(images.router)

# app = FastAPI()


