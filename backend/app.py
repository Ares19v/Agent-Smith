"""
app.py
======
FastAPI application factory for Agent Smith.

Mounts:
  /static      — CSS and JavaScript assets.
  /api/*       — REST endpoints (see api.py).
  /            — Serves index.html (SPA shell).

Also configures:
  - CORS (permissive for local development; replace '*' with your domain in prod).
  - Lifespan context manager for startup / shutdown events.
  - Request timing middleware (X-Process-Time-Ms header).
  - Global exception handler for clean JSON error responses.
"""

import logging
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else (safe no-op if file absent)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api import router as api_router

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("AgentSmith.App")


# ─── Lifespan ─────────────────────────────────────────────────────────────────
# Replaces deprecated @app.on_event("startup") / ("shutdown") hooks.
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("═══ Agent Smith v2.0.0 — Server Online ═══")
    yield
    logger.info("═══ Agent Smith — Shutting Down ═══")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Agent Smith",
    description=(
        "A modular, local-first AI orchestration platform. "
        "Create custom intent-based agents, chat with them, and inject "
        "document context — all running entirely on your machine."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Agent Smith",
        "url": "https://github.com/Ares19v/Agent-Smith",
    },
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Permissive for local development.
# Production: replace allow_origins=["*"] with your specific domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Timing Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Injects X-Process-Time-Ms into every response for latency monitoring."""
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{elapsed:.2f}"
    return response


# ─── Global Exception Handler ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches unhandled exceptions and returns a consistent JSON error body."""
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "error": str(exc)},
    )


# ─── Routes ───────────────────────────────────────────────────────────────────
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
app.include_router(api_router)


@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the SPA shell (index.html)."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
