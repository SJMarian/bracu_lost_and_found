from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./blf.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    from app.models.user_model import User
    from app.models.item_model import Item
    SQLModel.metadata.create_all(engine)

