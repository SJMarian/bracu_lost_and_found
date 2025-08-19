from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id") 
    user_id: int = Field(foreign_key="user.id")  
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
