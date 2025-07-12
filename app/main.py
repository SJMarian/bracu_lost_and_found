from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import init_db
from app.controllers import auth_controller, home_controller, item_details_controller

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="8dKy9eSAtJQ3MPsutGZUEfAUqahEGQDp")

# Initialize the database
init_db()


# Mount static directory (for CSS/JS/images if any)
app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Register controller (routes)
app.include_router(auth_controller.router)
app.include_router(home_controller.router)
app.include_router(item_details_controller.router)