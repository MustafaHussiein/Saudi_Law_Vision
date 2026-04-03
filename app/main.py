"""
Main FastAPI Application Entry Point
File: app/main.py

FIX: exception_handlers must be CALLABLES (functions), not dicts
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.endpoints.llm import router as llm_router

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("app.main")


# ─── Exception Handlers (must be FUNCTIONS, not dicts) ────────────────────────

async def not_found_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Custom 404 handler"""
    # Try to return HTML page first
    try:
        templates = Jinja2Templates(directory="templates")
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=404
        )
    except Exception:
        return JSONResponse(
            status_code=404,
            content={"detail": "الصفحة غير موجودة - Not Found"}
        )


async def forbidden_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Custom 403 handler"""
    try:
        templates = Jinja2Templates(directory="templates")
        return templates.TemplateResponse(
            "errors/403.html",
            {"request": request},
            status_code=403
        )
    except Exception:
        return JSONResponse(
            status_code=403,
            content={"detail": "غير مصرح - Forbidden"}
        )


async def server_error_handler(request: Request, exc: Exception) -> HTMLResponse:
    """Custom 500 handler"""
    logger.error(f"Server error: {exc}")
    try:
        templates = Jinja2Templates(directory="templates")
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request},
            status_code=500
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "خطأ في الخادم - Internal Server Error"}
        )


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    """Handle all HTTPExceptions"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    
    # For web pages (non-API), return HTML error pages
    if not request.url.path.startswith("/api"):
        try:
            templates = Jinja2Templates(directory="templates")
            if exc.status_code == 404:
                return templates.TemplateResponse(
                    "errors/404.html",
                    {"request": request},
                    status_code=404
                )
            elif exc.status_code == 403:
                return templates.TemplateResponse(
                    "errors/403.html",
                    {"request": request},
                    status_code=403
                )
        except Exception:
            pass
    
    # For API routes, return JSON
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """Handle request validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "خطأ في البيانات المدخلة",
            "errors": exc.errors()
        }
    )


# ─── App Factory ──────────────────────────────────────────────────────────────

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Legal Tech Platform - Riada Law",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        redirect_slashes=False,
    )

    # ── CORS Middleware ────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers (pass FUNCTIONS, not dicts!) ───────────────────────
    from fastapi.exceptions import RequestValidationError, HTTPException
    import os

    # Get the root directory (E:\Previous work\Amad AlOula)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(404, not_found_handler)
    app.add_exception_handler(403, forbidden_handler)
    app.add_exception_handler(500, server_error_handler)

    # ── Static Files ──────────────────────────────────────────────────────────
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
        # In app/main.py, ensure this is present:
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
        app.mount("/laws", StaticFiles(directory=os.path.join(BASE_DIR, "SaudiLaw")), name="laws")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")

    # ── Create DB Tables ──────────────────────────────────────────────────────
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")

    # ── Routers ───────────────────────────────────────────────────────────────
    # API routes
    try:
        from app.api.v1.api import api_router
        app.include_router(api_router, prefix=settings.API_V1_STR)
        app.include_router(llm_router, prefix="/api/v1/llm", tags=["AI"])
        logger.info("✅ API routes loaded")
    except Exception as e:
        logger.error(f"❌ Could not load API routes: {e}")

    # Web routes (Jinja2 templates)
    try:
        from app.web.routes import web_router
        app.include_router(web_router)
        logger.info("✅ Web routes loaded")
    except Exception as e:
        logger.error(f"❌ Could not load web routes: {e}")

    # ── Root redirect ──────────────────────────────────────────────────────────
    from fastapi.responses import RedirectResponse

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/dashboard")

    # ── Startup / Shutdown events ──────────────────────────────────────────────
    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 60)
        logger.info(f"🚀 {settings.PROJECT_NAME} starting...")
        logger.info(f"📡 API docs: http://localhost:{settings.PORT}/api/docs")
        logger.info(f"🌐 App:      http://localhost:{settings.PORT}/dashboard")
        logger.info("=" * 60)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("🛑 Server shutting down...")

    return app


# ─── Create App ───────────────────────────────────────────────────────────────
app = create_application()


# ─── Run directly ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )