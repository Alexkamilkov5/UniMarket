from typing import Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


# model dlya logina
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str


# 6 mashgulot uchun itemlar uchun schema
try:
    # from pydantic import ConfigDict

    _V2 = True
except Exception:
    _V2 = False


# class ItemCreate(BaseModel):
#     name: str = Field(..., min_length=1, json_schema_extra={"example": "Laptop"})
#     description: Optional[str] = Field(
#         None, max_length=500, json_schema_extra={"example": "Gaming laptop"}
#     )
#     price: float = Field(..., gt=0, json_schema_extra={"example": 1200.50})


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, json_schema_extra={"example": "New Laptop"}
    )
    description: Optional[str] = Field(
        None, max_length=500, json_schema_extra={"example": "Updated description"}
    )
    price: Optional[float] = Field(None, gt=0, json_schema_extra={"example": 1500.00})


# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     description: Optional[str]
#     price: float


#     model_config = ConfigDict(
#         from_attributes=True
#     )  # Позволяет строить модель из ORM-объектов
# 5 hafta uchun schemalar
class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)
    # class Config:
    #     from_attributes = True  # pydantic v2


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
    # class Config:
    #     from_attributes = True # pydantic v2


class PageItems(BaseModel):
    items: Sequence[ItemResponse]
    total: int
    limit: int
    offset: int
    next_offset: Optional[int] = None
