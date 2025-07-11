from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

@router.get("/", response_class=HTMLResponse)
def show_landing(request: Request):
    return templates.TemplateResponse("auth_page.html", {"request": request})
