import boto3
from fastapi import FastAPI, HTTPException
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from config import *
from fastapi.responses import StreamingResponse

app = FastAPI()

# Initialize AWS S3 client
s3_client = boto3.client(
    "s3",
    # Provide your AWS credentials and region
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME
)


def merge_images(image1_path: str, image2_path: str, text: str = "TEXT"):
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
        final_image = merge_images_with_text(merged_image, text)

        # Convert the merged image to bytes
        output_buffer = BytesIO()
        final_image.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        # Return the merged image as bytes
        return output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def merge_images_with_text(image, text="TEXT", font_path="Fjord_Regular.ttf", font_size=70, text_color=(1, 5, 28)):
    # Add text at the bottom
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()

    # Estimate the text width (assuming average character width around half the font size)
    average_char_width = font_size * 0.6
    estimated_text_width = len(text) * average_char_width

    # Center the text horizontally
    width, height = image.size
    text_position = ((width - estimated_text_width) // 2, height - 160)  # Keep vertical position

    # Draw the text in specified color
    draw.text(text_position, text, fill=text_color, font=font)

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


@app.post("/merge_and_upload")
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



@app.post("/merge_and_view")
async def merge_and_upload(image1_path: str, image2_path: str, text: str = "TEXT"):
    try:
        # Merge images
        merged_image_bytes = merge_images(image1_path, image2_path, text)

        # Return the merged image directly as a response
        return StreamingResponse(BytesIO(merged_image_bytes), media_type="image/png")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

