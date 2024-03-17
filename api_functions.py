import requests
from PIL import Image
from io import BytesIO

def download_image_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            return None
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None
