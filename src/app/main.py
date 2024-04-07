# Import required modules
from fastapi import FastAPI, Security, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

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

# Load API keys and permissions from environment variables
API_KEYS_PERMISSIONS = {}
for key, value in os.environ.items():
    if key.startswith("API_KEY_"):
        api_key = value
        permissions_key = f"{key}_PERMISSIONS"
        permissions = os.getenv(permissions_key, "").split(",")
        API_KEYS_PERMISSIONS[api_key] = permissions

# Define the api_key_query function to extract API key from query parameters
async def api_key_query(api_key: str = Query(..., description="API key")):
    return api_key

# API key authentication middleware
async def api_key_auth(api_key: str = Security(api_key_query, scopes=[])):
    if api_key not in API_KEYS_PERMISSIONS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Check if the requested endpoint requires a specific permission
    required_permission = API_KEYS_PERMISSIONS[api_key]
    requested_permission = "read"  # Example: You can modify this based on your endpoint logic

    if requested_permission not in required_permission:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

# Import routers after defining the necessary middleware
from .api.api_v0.api import router as api_v0_router

# Include routers with dependencies for API key authentication
app.include_router(api_v0_router, prefix="/api/v0", dependencies=[Security(api_key_auth)])
