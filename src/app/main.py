from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv
import os
# Import routers
from .api.api_v0.api import router as api_v0_router
from .api.api_v0.functions import web3_functions as web3
from datetime import datetime
# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(api_v0_router, prefix="/api/v0")

# Enable Mangum for AWS Lambda integration
handler = Mangum(app)

#
# from fastapi import FastAPI
#
# app = FastAPI()
#
#
# @app.get("/")
# def get_root():
#     return {"message": "FastAPI running in a Docker container"}

