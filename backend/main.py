"""
Main FastAPI application entry point for EQIA (Environmental Quality Intelligence Assistant)
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Import routers
from api.route.agent_router import router as agent_router

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    print("🚀 Starting EQIA Backend Server...")
    print("🌱 Environmental Quality Intelligence Assistant")
    print("📊 Ready to analyze water and soil quality data")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down EQIA Backend Server...")

# Create FastAPI application
app = FastAPI(
    title="EQIA - Environmental Quality Intelligence Assistant",
    description="AI-powered assistant for environmental monitoring and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        # Add your frontend domain in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent_router, prefix="/api", tags=["Agent"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EQIA - Environmental Quality Intelligence Assistant",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EQIA Backend",
        "timestamp": os.environ.get("DEPLOYMENT_TIME", "development")
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": f"The requested path '{request.url.path}' was not found",
            "available_endpoints": [
                "/",
                "/health", 
                "/api/agent/chat",
                "/api/agent/chat/stream",
                "/api/agent/health",
                "/api/agent/tools",
                "/docs",
                "/redoc"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "status": "error"
        }
    )

if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🌟 Starting EQIA Backend on {host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if not debug else "debug",
        access_log=True
    )
