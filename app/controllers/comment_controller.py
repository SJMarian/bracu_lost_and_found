from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.models.comment_model import Comment
from app.models.user_model import User
from app.database import engine
from app.contants import ITEM_DETAILS_PATH
from app.di import get_current_user

router = APIRouter()

# Add a comment
@router.post("/item/{item_id}/comment")
def add_comment(
    item_id: int,
    comment_text: str = Form(...),
    user: dict = Depends(get_current_user)
):
    with Session(engine) as session:
        new_comment = Comment(
            item_id=item_id,
            user_id=user["id"],
            text=comment_text
        )
        session.add(new_comment)
        session.commit()

    return RedirectResponse(url=f"/item/{item_id}", status_code=303)

