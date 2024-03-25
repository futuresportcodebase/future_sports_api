import requests
from urllib.parse import urlparse
import boto3
from fastapi import HTTPException
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from ..config import *


# Initialize AWS S3 client
s3_client = boto3.client(
    "s3",
    # Provide your AWS credentials and region
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


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
