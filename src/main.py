from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.templating import Jinja2Templates
import uvicorn

from src.config import settings
from src.database import engine
from src.admin.setup import setup_admin
from src.catalog.router import router as catalog_router
from src.pages.router import router as pages_router
from src.feedback.router import router as feedback_router

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

is_production = not settings.DEBUG
docs_url = "/docs" if settings.DEBUG else None
redoc_url = "/redoc" if settings.DEBUG else None

app = FastAPI(
    title=settings.APP_NAME,
    docs_url=docs_url,
    redoc_url=redoc_url,
    middleware=[
        Middleware(
            SessionMiddleware, 
            secret_key=settings.SECRET_KEY,
            https_only=is_production,
            same_site="lax"
        )
    ]
)
setup_admin(app, engine)

app.include_router(catalog_router)
app.include_router(pages_router)
app.include_router(feedback_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request}, 
            status_code=404 
        )
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True, host=settings.HOST, port=8090, server_header=False)