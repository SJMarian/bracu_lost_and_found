from sqlmodel import SQLModel, Field

class ItemClaim(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    item_id: int
    claim_by: int
    claim_date: str
