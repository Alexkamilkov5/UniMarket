# app/schemas.py
from typing import Optional, Sequence

from pydantic import BaseModel, ConfigDict, Field


# -----------------------
# Auth / User schemas
# -----------------------
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    # опционально можно указывать роль при создании (удобно для тестов/админов)
    role: str = Field("user", description="user или admin")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    username: str
    role: str = "user"

    model_config = ConfigDict(from_attributes=True)


# -----------------------
# Category schemas (неделя 5)
# -----------------------
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# -----------------------
# Item schemas
# -----------------------
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, json_schema_extra={"example": "Laptop"})
    description: Optional[str] = Field(
        None, max_length=500, json_schema_extra={"example": "Gaming laptop"}
    )
    price: float = Field(..., gt=0, json_schema_extra={"example": 1200.5})
    category_id: Optional[int] = Field(None, description="ID категории (optional)")


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, json_schema_extra={"example": "New Laptop"}
    )
    description: Optional[str] = Field(
        None, max_length=500, json_schema_extra={"example": "Updated description"}
    )
    price: Optional[float] = Field(None, gt=0, json_schema_extra={"example": 1500.0})
    category_id: Optional[int] = None


class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: Optional[int] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


# -----------------------
# Pagination response
# -----------------------
class PageItems(BaseModel):
    items: Sequence[ItemResponse]
    total: int
    limit: int
    offset: int
    next_offset: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserPublic):
    hashed_password: str
