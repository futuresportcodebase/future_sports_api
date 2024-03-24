from fastapi import APIRouter, Query
import os
from .endpoints import items, users, web3
import requests
from urllib.parse import urlparse
import boto3
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .config import *
from fastapi.responses import StreamingResponse
from datetime import datetime

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

# app = FastAPI()

# Initialize AWS S3 client
s3_client = boto3.client(
    "s3",
    # Provide your AWS credentials and region
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


def merge_images(
        image1_path: str = "s3://futuresportsimages/images/bafybeibfnwmpyd73f737jgr256wxr3wv35hlstvvmjyi4tf7ns3zzzeiue",
        image2_path: str = "s3://futuresportsimages/images/bafkreigymxzyva7uwtogbwlmxjcwonq2tyihd3fixt3t6y3nqjvkc5xdfa",
        header_text="HEADER", text="TEXT",
        font_path="app/api/api_v0/assets/Minercraftory.ttf", font_size=50, header_font_size=50,
        text_color=(250, 221, 177), header_color=(250, 221, 177),
        text_vertical_position=1100, header_vertical_position=140):
    try:
        # Assuming s3_client is already initialized as shown previously

        # Parse S3 paths
        image1_bucket, image1_key = image1_path.split("//")[1].split("/", 1)
        image2_bucket, image2_key = image2_path.split("//")[1].split("/", 1)

        # Download images from S3
        image1_obj = s3_client.get_object(Bucket=image1_bucket, Key=image1_key)
        image2_obj = s3_client.get_object(Bucket=image2_bucket, Key=image2_key)

        # Open images from S3 objects
        image1 = Image.open(BytesIO(image1_obj['Body'].read()))
        image2 = Image.open(BytesIO(image2_obj['Body'].read()))

        # Resize image1 to fit the dimensions of image2
        image1_resized = image1.resize(image2.size, Image.ANTIALIAS)

        # Paste image1_resized onto image2
        merged_image = image2.copy()
        merged_image.paste(image1_resized, (0, 0), image1_resized)

        # Utilize merge_images_with_text with all provided options
        final_image = merge_images_with_text(merged_image, header_text, text, font_path,
                                             font_size, header_font_size, text_color, header_color,
                                             text_vertical_position, header_vertical_position)

        # Convert the merged image to bytes
        output_buffer = BytesIO()
        final_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def merge_images_with_text(image, header_text="HEADER", text="TEXT",
                           font_path="app/api/api_v0/assets/Minercraftory.ttf",
                           font_size=50, header_font_size=50,
                           text_color=(250, 221, 177), header_color=(250, 221, 177),
                           text_vertical_position=1100, header_vertical_position=140):
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(font_path, font_size)
        header_font = ImageFont.truetype(font_path, header_font_size)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    width, height = image.size
    text_position = ((width - draw.textsize(text, font=font)[0]) // 2, text_vertical_position)
    header_position = ((width - draw.textsize(header_text, font=header_font)[0]) // 2, header_vertical_position)

    draw.text(header_position, header_text, fill=header_color, font=header_font)
    draw.text(text_position, text, fill=text_color, font=font)

    return image


def upload_to_s3(image_data: bytes, filename: str, bucket="futuresportsimages"):
    s3_object_key = f"output/{filename}"
    try:
        # Upload the merged image to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_object_key,
            Body=image_data,
            ContentType="image/png"  # Adjust content type as needed
        )
        # Return the URL of the uploaded image
        s3_object_url = f"https://{bucket}.s3.us-east-1.amazonaws.com/{filename}"
        return s3_object_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge_and_upload")
async def merge_and_upload(background: str = Query(
    "s3://futuresportsimages/images/bafybeibfnwmpyd73f737jgr256wxr3wv35hlstvvmjyi4tf7ns3zzzeiue"),
                           pfp: str = Query(
                               "s3://futuresportsimages/images/bafkreigymxzyva7uwtogbwlmxjcwonq2tyihd3fixt3t6y3nqjvkc5xdfa"),
                           header_text: str = Query("Header", description="Header Text"),
                           text: str = Query("TEXT", description="Main Text"),
                           font_path: str = Query("app/api/api_v0/assets/Minercraftory.ttf", description="Font Path"),
                           font_size: int = Query(50, description="Font Size for Main Text"),
                           header_font_size: int = Query(50, description="Font Size for Header Text"),
                           text_color: str = Query("(250, 221, 177)", description="Color of Main Text (R, G, B)"),
                           header_color: str = Query("(250, 221, 177)", description="Color of Header Text (R, G, B)"),
                           text_vertical_position: int = Query(1100, description="Vertical Position of Main Text"),
                           header_vertical_position: int = Query(140, description="Vertical Position of Header Text")):
    try:
        # Convert string tuples to actual tuples for colors
        text_color_tuple = tuple(map(int, text_color.strip("()").split(", ")))
        header_color_tuple = tuple(map(int, header_color.strip("()").split(", ")))

        # Check if image paths are URLs and handle accordingly
        # Ensure download_image_to_s3 function is implemented to handle this logic

        # Merge images with additional options
        merged_image_bytes = merge_images(background, pfp, header_text, text,
                                          font_path, font_size, header_font_size,
                                          text_color_tuple, header_color_tuple,
                                          text_vertical_position, header_vertical_position)

        # Upload merged image to S3 and generate a URL
        filename = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S") + "_merged_image.png"  # Updated for filename-safe string
        s3_object_url = upload_to_s3(merged_image_bytes, filename)

        return {"s3_object_url": s3_object_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def download_image_to_s3(image_url: str, bucket="futuresportsimages"):
    try:
        # Download image from URL
        response = requests.get(image_url)
        response.raise_for_status()

        # Upload image to S3
        filename = urlparse(image_url).path.split("/")[-1]  # Extract filename from URL
        s3_object_key = f"images/{filename}"  # Specify S3 object key
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_object_key,
            Body=response.content,
            ContentType=response.headers.get("content-type", "image/png")  # Set content type
        )
        return f"s3://{bucket}/{s3_object_key}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge_and_view")
async def merge_and_view(image1_path: str = Query(
                            "s3://futuresportsimages/images/bafybeibfnwmpyd73f737jgr256wxr3wv35hlstvvmjyi4tf7ns3zzzeiue"),
                         image2_path: str = Query(
                             "s3://futuresportsimages/images/bafkreigymxzyva7uwtogbwlmxjcwonq2tyihd3fixt3t6y3nqjvkc5xdfa"),
                         header_text: str = Query("Header"),
                         text: str = Query("TEXT"),
                         font_path: str = Query("app/api/api_v0/assets/Minercraftory.ttf"),
                         font_size: int = Query(50),
                         header_font_size: int = Query(50),
                         text_color: str = Query("(250, 221, 177)"),  # Expecting RGB tuple as string
                         header_color: str = Query("(250, 221, 177)"),  # Expecting RGB tuple as string
                         text_vertical_position: int = Query(1100),
                         header_vertical_position: int = Query(140)):
    try:
        # Convert string tuples to actual tuples for colors
        text_color_tuple = tuple(map(int, text_color.strip("()").split(", ")))
        header_color_tuple = tuple(map(int, header_color.strip("()").split(", ")))

        # Check if image paths are URLs and handle accordingly
        # This logic remains unchanged but ensure it's correctly implemented

        # Merge images with additional options
        merged_image_bytes = merge_images(image1_path, image2_path, header_text, text,
                                          font_path, font_size, header_font_size,
                                          text_color_tuple, header_color_tuple,
                                          text_vertical_position, header_vertical_position)

        # Return the merged image directly as a response
        return StreamingResponse(BytesIO(merged_image_bytes), media_type="image/png")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
