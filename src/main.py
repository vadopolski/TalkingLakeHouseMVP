"""
Main FastAPI application entry point.

Sales & Website Analytics Chat Assistant MVP
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.sales_endpoint import create_sales_router
from config.settings import get_settings


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI app instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Natural language interface for sales and website analytics"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers
    )

    # Include routers
    sales_router = create_sales_router()
    app.include_router(sales_router)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Sales & Website Analytics Chat Assistant API",
            "version": settings.app_version,
            "status": "operational"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.app_name
        }

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
