from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.controllers import auth_controller, home_controller

app = FastAPI()

# Initialize the database
init_db()

# Mount static directory (for CSS/JS/images if any)
app.mount("/assets", StaticFiles(directory="app/assets"), name="assets")
app.mount("/images", StaticFiles(directory="app/images"), name="images")

# Register controller (routes)
app.include_router(auth_controller.router)
app.include_router(home_controller.router)