from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    contact_number: str
    image_path: str
    post_by: int
    handover_status: str
