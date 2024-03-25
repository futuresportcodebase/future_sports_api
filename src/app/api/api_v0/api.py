from typing import Tuple
from fastapi import APIRouter, Query
import os
from pydantic import BaseModel
from .endpoints import items, users, web3, images
import requests
from urllib.parse import urlparse
import boto3
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .config import *
from fastapi.responses import StreamingResponse
from datetime import datetime
from .functions.images_functions import download_image_to_s3, merge_images, upload_to_s3

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


