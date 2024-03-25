from typing import Tuple

from fastapi import APIRouter, Query
import os

from pydantic import BaseModel

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
