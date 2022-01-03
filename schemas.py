from typing import List
from pydantic import BaseModel as Schema

################################################################################
# pydantic schemas
################################################################################

class SchemaUser(Schema):
    """Схема описывает атрибуты пользователя.
    """
    id: int = None
    login: str
    password: str
    items: List["SchemaItem"] = []

    class Config:
        orm_mode = True


class SchemaItem(Schema):
    """Схема описывает атрибуты объекта.
    """
    id: int = None
    name: str
    owner_id: int
    owner: "SchemaUser" = None

    class Config:
        orm_mode = True
