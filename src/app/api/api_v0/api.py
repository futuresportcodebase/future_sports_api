from fastapi import APIRouter
import os
from .endpoints import items, users

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

import boto3
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from .config import *
from fastapi.responses import StreamingResponse

# app = FastAPI()

# Initialize AWS S3 client
s3_client = boto3.client(
    "s3",
    # Provide your AWS credentials and region
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


def merge_images(image1_path: str, image2_path: str,header_text="HEADER", text: str = "TEXT"):
    try:
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

        # Add text to the merged image
        final_image = merge_images_with_text(merged_image,header_text, text)

        # Convert the merged image to bytes
        output_buffer = BytesIO()
        final_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        # Return the merged image as bytes
        return output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def merge_images_with_text(image, header_text="HEADER", text="TEXT", font_path="api/api_v0/assets/Minercraftory.ttf", font_size=50, header_font_size=40,
                           text_color=(1, 8, 33), header_color=(250, 221, 177)):
    # Add text at the bottom
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
        header_font = ImageFont.truetype(font_path, header_font_size)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    # Calculate text size
    text_width, text_height = draw.textsize(text, font=font)
    header_text_width, header_text_height = draw.textsize(header_text, font=header_font)

    # Center the text horizontally
    width, height = image.size
    text_position = ((width - text_width) // 2, height - 153)  # Adjust vertical position as needed

    # Draw the text in specified color
    draw.text(text_position, text, fill=text_color, font=font)

    # Position the header text at the top
    header_text_position = ((width - header_text_width) // 2, 140)  # Adjust vertical position as needed

    # Draw the header text in specified color
    draw.text(header_text_position, header_text, fill=header_color, font=header_font)

    return image





def upload_to_s3(image_data: bytes, filename: str):
    try:
        # Upload the merged image to S3
        s3_client.put_object(
            Bucket="futuresportsimages",
            Key= "output/" + filename,
            Body=image_data,
            ContentType="image/png"  # Adjust content type as needed
        )
        # Return the URL of the uploaded image
        s3_object_url = f"https://futuresportsimages.s3.us-east-1.amazonaws.com/{filename}"
        return s3_object_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge_and_upload")
async def merge_and_upload(image1_path: str, image2_path: str, text: str = "TEXT"):
    try:
        # Merge images
        merged_image_bytes = merge_images(image1_path, image2_path, text)
        # Upload merged image to S3
        filename = "merged_image.png"  # Specify a filename for the merged image
        s3_object_url = upload_to_s3(merged_image_bytes, filename)
        return {"s3_object_url": s3_object_url}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/merge_and_view")
async def merge_and_upload(image1_path: str = "s3://futuresportsimages/testImages/SMB_monkey-test-PFP.png",
                           image2_path: str = "s3://futuresportsimages/BallStarsBaseballEditionZero/BallStars-Baseball-Edition-0_EARTH-BOSTON_base_t1.png",
                           header_text: str = "Header",
                           text: str = "TEXT"):
    try:
        # Merge images
        merged_image_bytes = merge_images(image1_path, image2_path, header_text=header_text, text=text)

        # Return the merged image directly as a response
        return StreamingResponse(BytesIO(merged_image_bytes), media_type="image/png")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


