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
from app.di import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

upload_folder = "uploads"
os.makedirs(upload_folder, exist_ok=True)


@router.get(HOME_PATH, response_class=HTMLResponse)
def home_page(request: Request, user: dict = Depends(get_current_user)):
    user_id = user['id']
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
async def submit_item(
    itemName: str = Form(...),
    itemDescription: str = Form(...),
    contactNumber: str = Form(...),
    image: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    user_id = user['id']
   

    filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = os.path.join(upload_folder, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await image.read())

    with Session(engine) as session:
        new_item = Item(
            name=itemName,
            description=itemDescription,
            contact=contactNumber,
            image_path=filename,
            post_by=user_id,
            handover_status="PENDING"
        )
        session.add(new_item)
        session.commit()

    return RedirectResponse(HOME_PATH, status_code=303)