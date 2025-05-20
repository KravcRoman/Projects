from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # If needed

from app.api.v1 import endpoints as v1_endpoints
from app.core.config import settings

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # Standard OpenAPI path
    version="1.0.0" # Or read from config/pyproject.toml
)

# Optional: Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the API router
app.include_router(
    v1_endpoints.router,
    prefix=f"{settings.API_V1_STR}/vacations", # Set base path for vacation endpoints
    tags=["Vacations"] # Tag for OpenAPI documentation grouping
)

# Root endpoint for health check
@app.get("/", tags=["Health Check"])
async def read_root():
    """Basic health check endpoint."""
    return {"status": "OK", "message": f"Welcome to {settings.PROJECT_NAME}!"}

# Add startup/shutdown events if needed (e.g., DB checks)
# @app.on_event("startup")
# async def on_startup():
#     print("Application startup...")
#     # await check_db_connection() # Example

# @app.on_event("shutdown")
# async def on_shutdown():
#     print("Application shutdown...")