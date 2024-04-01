from fastapi import FastAPI, Security, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
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

# Define the expected API key
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise EnvironmentError("API_KEY environment variable not set")


# Define the api_key_query function to extract API key from query parameters
async def api_key_query(api_key: str = Query(..., description="API key")):
    return api_key


# API key authentication middleware
async def api_key_auth(api_key: str = Security(api_key_query, scopes=[])):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


# Import routers after defining the necessary middleware
from .api.api_v0.api import router as api_v0_router

# Include routers with dependencies for API key authentication
app.include_router(api_v0_router, prefix="/api/v0", dependencies=[Security(api_key_auth)])

