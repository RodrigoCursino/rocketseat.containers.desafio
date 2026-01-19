from pydantic import BaseModel
from typing import Optional


class ProductSchema(BaseModel):

    id: Optional[int]
    name: str
    price: float

    class Config:
        orm_mode = True


