from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import ingest, search, synthesize, trends
import logging, time

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Research Intelligence Agent", version="1.0")
app.include_router(ingest.router,      prefix="/ingest",     tags=["ingestion"])
app.include_router(search.router,      prefix="/search",     tags=["search"])
app.include_router(synthesize.router,  prefix="/synthesize", tags=["synthesis"])
app.include_router(trends.router,      prefix="/trends",     tags=["trends"])

@app.middleware("http")
async def log_requests(request: Request, call_next):
    t = time.time()
    r = await call_next(request)
    logger.info(f"{request.method} {request.url.path} → {r.status_code} ({round((time.time()-t)*1000)}ms)")
    return r

@app.exception_handler(Exception)
async def global_error(request: Request, exc: Exception):
    logger.error(f"Error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": str(exc)})