from fastapi import APIRouter, Request, Depends, Form, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.item_model import Item
from app.models.user_model import User
from app.database import engine
from sqlmodel import select, Session
import shutil
import uuid
from app.contants import HOME_PATH
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

def get_current_user_id(request: Request):
    return request.session.get("user_id")

@router.get(HOME_PATH, response_class=HTMLResponse)
def home_page(request: Request):
    user_id = get_current_user_id(request=request)
    with Session(engine) as session:
        my_items = session.exec(
            select(Item).where(Item.post_by == user_id, Item.handover_status == "PENDING")
        ).all()

        other_items = session.exec(
            select(Item).where(Item.post_by != user_id, Item.handover_status == "PENDING")
        ).all()

    return templates.TemplateResponse("home_page.html", {
        "request": request,
        "my_items": my_items,
        "other_items": other_items
    })

@router.post("/submit-item")
def submit_item(
    itemName: str = Form(...),
    itemDescription: str = Form(...),
    contactNumber: str = Form(...),
    image: UploadFile = File(...),
):
    user_id = get_current_user_id()
    upload_dir = "/static/Images"
    os.makedirs(upload_dir, exist_ok=True) 

    filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    with Session(engine) as session:
        new_item = Item(
            name=itemName,
            description=itemDescription,
            contact_number=contactNumber,
            image_path=filename,
            post_by=user_id,
            handover_status="PENDING"
        )
        session.add(new_item)
        session.commit()

    return RedirectResponse(HOME_PATH, status_code=303)