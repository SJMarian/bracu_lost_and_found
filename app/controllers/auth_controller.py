from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.contants import LOGIN_PATH, HOME_PATH, REGISTRATION_PATH
from app.models.user_model import User
from sqlmodel import Session, select
from app.database import engine

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

@router.get(LOGIN_PATH, response_class=HTMLResponse)
def login_page(request: Request, error: str = None, success: str = None):
    return templates.TemplateResponse("login_page.html", {"request": request, "error": error, "success": success})

@router.get(REGISTRATION_PATH, response_class=HTMLResponse)
def registration_page(request: Request, error: str = None, success: str = None):
    return templates.TemplateResponse("registration_page.html", {"request": request, "error": error, "success": success})


@router.post("/login")
def handle_login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = get_user(email, password)
    if user:
        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role" : user.role
        }
        return RedirectResponse(url=HOME_PATH, status_code=303)
    else:
        return RedirectResponse(url=LOGIN_PATH+"?error=Invalid email or password", status_code=303)

@router.post("/registration")
def handle_registration(email: str = Form(...), password: str = Form(...), name: str = Form(...), phone: str = Form(...), student_id: str = Form(...)):
    if get_user_by_email(email):
        return RedirectResponse(url=REGISTRATION_PATH+"?error=User already exists", status_code=303)
    else:
        user = User(email=email, password=password, name=name, phone=phone, student_id=student_id, role="STUDENT")
        with Session(engine) as session:
            session.add(user)
            session.commit()
        return RedirectResponse(url=LOGIN_PATH+"?success=Registration successful", status_code=303)


# Find a user
def get_user(email: str, password: str) -> User | None:
    with Session(engine) as session:
        statement = select(User).where(User.email == email and User.password == password)
        result = session.exec(statement).first()
        return result

def get_user_by_email(email: str) -> User | None:
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        result = session.exec(statement).first()
        return result