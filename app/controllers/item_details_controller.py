from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from app.models.item_model import Item
from app.models.item_claim_model import ItemClaim
from app.models.handover_items_model import HandoverItems
from app.models.user_model import User
from app.database import engine
from datetime import datetime
from app.contants import HOME_PATH, ITEM_DETAILS_PATH

router = APIRouter()
templates = Jinja2Templates(directory="app/views")


# Dummy session-based user getter
def get_current_user(request: Request):
    return request.session.get("user")


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


        claims = session.exec(
            select(User.id, User.name, User.phone, ItemClaim.claim_date)
            .join(ItemClaim, ItemClaim.claim_by == User.id)
            .where(ItemClaim.item_id == item_id)
        ).all()

        return templates.TemplateResponse("item_details_page.html", {
            "request": request,
            "item": item,
            "user": user,
            "is_claimed": is_claimed,
            "claims": claims
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
