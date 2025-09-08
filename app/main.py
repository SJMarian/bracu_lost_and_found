from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import init_db
from app.controllers import auth_controller, home_controller, item_details_controller, comment_controller
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="8dKy9eSAtJQ3MPsutGZUEfAUqahEGQDp")
templates = Jinja2Templates(directory="app/views")

# Initialize the database
init_db()


# Mount static directory (for CSS/JS/images if any)
app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register controller (routes)
app.include_router(auth_controller.router)
app.include_router(home_controller.router)
app.include_router(item_details_controller.router)
app.include_router(comment_controller.router)


# custom 404 handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html", {"request": request}, status_code=404
        )
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)