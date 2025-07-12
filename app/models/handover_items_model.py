from sqlmodel import SQLModel, Field
from datetime import datetime

class HandoverItems(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    handover_by: int
    handover_to: int
    item_id: int
    date: str = Field(default_factory=lambda: datetime.now().isoformat())