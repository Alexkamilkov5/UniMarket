from pydantic import BaseModel, Field


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
    from pydantic import ConfigDict

    _V2 = True
except Exception:
    _V2 = False
# class ItemCreate(BaseModel):
#     name: str = Field(..., min_length=1, example="Laptop")
#     description: str | None = Field(None, example="Gaming laptop")
#     price: float = Field(..., gt=0, example=1200.50)


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = Field(None)
    price: float = Field(..., gt=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Laptop", "description": "Gaming laptop", "price": 1200.50}
            ]
        }
    }


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    if _V2:
        model_config = ConfigDict(from_attributes=True)
    else:

        class Config:
            orm_mode = True
