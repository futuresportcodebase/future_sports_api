import boto3
from fastapi import FastAPI, HTTPException
from PIL import Image
from io import BytesIO
from config import *

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
        print(image1_bucket, image1_key)
        image2_bucket, image2_key = image2_path.split("//")[1].split("/", 1)

        # Download images from S3
        image1_obj = s3_client.get_object(Bucket=image1_bucket, Key=image1_key)
        image2_obj = s3_client.get_object(Bucket=image2_bucket, Key=image2_key)

        # Open images from S3 objects
        image1 = Image.open(BytesIO(image1_obj['Body'].read()))
        image2 = Image.open(BytesIO(image2_obj['Body'].read()))

        # Merge the images
        # Your merge logic here

        # Example merge logic (pasting image2 onto image1)
        image1.paste(image2, (0, 0), image2)

        # Convert the merged image to bytes
        output_buffer = BytesIO()
        image1.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        # Return the merged image as bytes
        return output_buffer.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        s3_object_url = f"https://YOUR_S3_BUCKET_NAME.s3.YOUR_AWS_REGION_NAME.amazonaws.com/{filename}"
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
