from datetime import datetime
from io import BytesIO
from typing import Tuple

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from ..functions.images_functions import download_image_to_s3, merge_images, upload_to_s3
router = APIRouter(prefix='/images', tags=["IMAGES"])

class MergeImageInput(BaseModel):
    background: str = "https://nftstorage.link/ipfs/bafybeibfnwmpyd73f737jgr256wxr3wv35hlstvvmjyi4tf7ns3zzzeiue"
    pfp: str = "https://nftstorage.link/ipfs/bafkreigymxzyva7uwtogbwlmxjcwonq2tyihd3fixt3t6y3nqjvkc5xdfa"
    header_text: str = "Header"
    text: str = "TEXT"
    font_path: str = "app/api/api_v0/assets/Minercraftory.ttf"
    font_size: int = 50
    header_font_size: int = 50
    text_color: Tuple[int, int, int] = (250, 221, 177)
    header_color: Tuple[int, int, int] = (250, 221, 177)
    text_vertical_position: int = 1100
    header_vertical_position: int = 140


@router.post("/merge_and_upload")
async def merge_and_upload(input_data: MergeImageInput):
    try:
        # Check if image paths are URLs and handle accordingly
        if input_data.pfp.startswith("http://") or input_data.pfp.startswith("https://"):
            # Download image from URL and upload to S3
            pfp = download_image_to_s3(input_data.pfp)
        else:
            pfp = input_data.pfp  # Assume it's already an S3 path

        if input_data.background.startswith("http://") or input_data.background.startswith("https://"):
            # Download image from URL and upload to S3
            background = download_image_to_s3(input_data.background)
        else:
            background = input_data.background  # Assume it's already an S3 path

        # Merge images with additional options
        merged_image_bytes = merge_images(background, pfp, input_data.header_text, input_data.text,
                                          input_data.font_path, input_data.font_size, input_data.header_font_size,
                                          input_data.text_color, input_data.header_color,
                                          input_data.text_vertical_position, input_data.header_vertical_position)

        # Upload merged image to S3 and generate a URL
        filename = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + "_merged_image.png"  # Updated for filename-safe string
        s3_object_url = upload_to_s3(merged_image_bytes, filename)

        return {"s3_object_url": s3_object_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge_and_view")
async def merge_and_view(input_data: MergeImageInput):
    try:
        if input_data.background.startswith("http://") or input_data.background.startswith("https://"):
            # Download image from URL and upload to S3
            input_data.background = download_image_to_s3(input_data.background)
        if input_data.pfp.startswith("http://") or input_data.pfp.startswith("https://"):
            # Download image from URL and upload to S3
            input_data.pfp = download_image_to_s3(input_data.pfp)

        # Merge images with additional options
        merged_image_bytes = merge_images(input_data.background, input_data.pfp,
                                          input_data.header_text, input_data.text,
                                          input_data.font_path, input_data.font_size, input_data.header_font_size,
                                          input_data.text_color, input_data.header_color,
                                          input_data.text_vertical_position, input_data.header_vertical_position)

        # Return the merged image directly as a response
        return StreamingResponse(BytesIO(merged_image_bytes), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
