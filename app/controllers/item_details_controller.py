from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.models.item_model import Item
from app.models.item_claim_model import ItemClaim
from app.models.handover_items_model import HandoverItems
from app.models.user_model import User
from app.models.comment_model import Comment
from app.database import engine
from datetime import datetime
from app.contants import HOME_PATH, ITEM_DETAILS_PATH
from app.di import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

# helper method to get time delta
def time_ago(dt: datetime) -> str:
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    months = days // 30
    years = days // 365

    if seconds < 60:
        return f"{int(seconds)} sec ago"
    elif minutes < 60:
        return f"{int(minutes)} min ago"
    elif hours < 24:
        return f"{int(hours)} hr ago"
    elif days < 30:
        return f"{int(days)} day ago"
    elif months < 12:
        return f"{int(months)} month ago"
    else:
        return f"{int(years)} year ago"




@router.get("/item/{item_id}", response_class=HTMLResponse)
def item_details(item_id: int, request: Request, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
       
        item = session.exec(select(Item).where(Item.id == item_id)).first()
        if not item:
            return templates.TemplateResponse("item_details_page.html", {"request": request, "item": None})

        is_claimed = session.exec(
            select(ItemClaim).where(
                ItemClaim.item_id == item_id,
                ItemClaim.claim_by == user["id"]
            )
        ).first() is not None

        # Get all claims
        claims = session.exec(
            select(User.id, User.name, User.phone, ItemClaim.claim_date)
            .join(ItemClaim, ItemClaim.claim_by == User.id)
            .where(ItemClaim.item_id == item_id)
        ).all()

         # Get all comments with user info
        comments = session.exec(
            select(Comment, User)
            .join(User, User.id == Comment.user_id)
            .where(Comment.item_id == item_id)
            .order_by(Comment.created_at.desc())
        ).all()

        # Format comments for easy use in template
        comments_data = [
            {
                "id": c.id,
                "text": c.text,
                "created_at": c.created_at,
                "user_id": u.id,
                "user_name": u.name,
                "time_pass": time_ago(c.created_at),
                "user_avatar": f"https://api.dicebear.com/9.x/fun-emoji/svg?seed={u.id}"
            }
            for c, u in comments
        ]


        return templates.TemplateResponse("item_details_page.html", {
            "request": request,
            "item": item,
            "user": user,
            "is_claimed": is_claimed,
            "claims": claims,
            "comments": comments_data
        })


@router.post("/item/delete/{item_id}")
def delete_item(item_id: int, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item and (item.post_by == user["id"] or user["role"] == "ADMIN"):
            session.delete(item)
            session.commit()
    return RedirectResponse(url=HOME_PATH, status_code=303)



@router.post("/item/claim/{item_id}")
def claim_item(item_id: int, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        # Check if already claimed to prevent duplicates
        existing_claim = session.exec(
            select(ItemClaim).where(ItemClaim.item_id == item_id, ItemClaim.claim_by == user["id"])
        ).first()
        if not existing_claim:
            claim = ItemClaim(item_id=item_id, claim_by=user["id"])
            session.add(claim)
            session.commit()
    return RedirectResponse(url=f"/item/{item_id}", status_code=303)


@router.post("/item/unclaim/{item_id}")
def unclaim_item(item_id: int, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        claim = session.exec(
            select(ItemClaim).where(ItemClaim.item_id == item_id, ItemClaim.claim_by == user["id"])
        ).first()
        if claim:
            session.delete(claim)
            session.commit()
    return RedirectResponse(url=f"/item/{item_id}", status_code=303)


@router.post("/item/handover/{item_id}")
def handover_item(
    request: Request,
    item_id: int,
    handover_to: int = Form(...),

    user: dict = Depends(get_current_user)
):
    with Session(engine) as session:
        # 1. Delete claim by current user
        claim = session.exec(
            select(ItemClaim).where(ItemClaim.item_id == item_id, ItemClaim.claim_by == user["id"])
        ).first()
        if claim:
            session.delete(claim)

        # 2. Insert into HandoverItems
        handover = HandoverItems(
            handover_by=user["id"],
            handover_to=handover_to,
            item_id=item_id,
            date=datetime.now().isoformat()
        )
        session.add(handover)
        session.commit()

        # 3. Update item status
        item = session.exec(select(Item).where(Item.id == item_id)).first()
        if item:
            item.handover_status = "DONE"
            session.add(item)
            session.commit()

    return RedirectResponse(url=HOME_PATH, status_code=303)


@router.post("/item/update/{item_id}")
async def update_item(
    item_id: int,
    itemName: str = Form(...),
    itemDescription: str = Form(...),
    contactNumber: str = Form(...),
    user: dict = Depends(get_current_user)
):
    user_id = user["id"]

    with Session(engine) as session:
        item = session.get(Item, item_id)

        if not item:
            return {"error": "Item not found"}
        if item.post_by != user_id and user["role"] != "ADMIN":
            return {"error": "Not authorized to edit this item"}

        item.name = itemName
        item.description = itemDescription
        item.contact = contactNumber

        session.add(item)
        session.commit()

    return RedirectResponse(HOME_PATH, status_code=303)