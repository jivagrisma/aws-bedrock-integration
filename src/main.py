"""
Main FastAPI application.

This module sets up the FastAPI application with routes and middleware
for the AWS Bedrock integration.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import llm_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AWS Bedrock API",
    description="REST API for AWS Bedrock Claude integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura según tus necesidades
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm_routes.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)