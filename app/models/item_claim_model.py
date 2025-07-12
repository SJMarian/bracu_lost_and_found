from sqlmodel import SQLModel, Field
from datetime import datetime

class ItemClaim(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int
    claim_by: int
    claim_date: str = Field(default_factory=lambda: datetime.now().isoformat())
