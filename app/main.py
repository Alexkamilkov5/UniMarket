from typing import List  # stdlib (оставьте только если реально используете)
from typing import Optional, cast

from fastapi import Query  # third-party
from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password  # first-party
from app.config import ALGORITHM, SECRET_KEY
from app.deps import get_db
from app.models import Item, User
from app.schemas import (
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)

# Login endpoint -login uchun endpoint

# Endpoint to get current user info 7 punkt


app = FastAPI(title="UniMarket", version="0.1.0")


@app.get("/health")  # type: ignore[misc]
def health() -> dict[str, str]:
    return {"status": "ok"}


class HelloResponse(BaseModel):
    message: str = Field(..., examples=["Hello, Alice!"])


@app.get("/hello")  # type: ignore[misc]
def hello(name: str = Query("world")) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}


class VersionResponse(BaseModel):
    version: str


@app.get("/version")
def version() -> VersionResponse:
    return VersionResponse(version="0.1.0")


#   4 mashg'ulotni bajarish
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@app.post("/auth/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(username=request.username, password=hash_password(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}


@app.post("/auth/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):  # type: ignore[arg-type]
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


# Добавим тестовый защищённый маршрут:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hello, {current_user}. This is a protected route!"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = cast(Optional[str], payload.get("sub"))
        if username is None:
            raise credentials_exc
        return username
    except JWTError:
        raise credentials_exc


@app.get("/me", response_model=UserPublic)  # type: ignore[misc]
def read_me(
    current_username: str = Depends(get_current_username), db: Session = Depends(get_db)
) -> UserPublic:
    user = db.query(User).filter(User.username == current_username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserPublic(id=user.id, username=user.username)  # type: ignore[misc]


# 6 mashgulot itemlar uchun endpointlar
@app.post("/items", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_username: str = Depends(get_current_username),  # убери если без токена
) -> ItemResponse:
    db_item = Item(name=item.name, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return ItemResponse.model_validate(db_item)


@app.get("/items", response_model=List[ItemResponse])
def list_items(db: Session = Depends(get_db)) -> List[ItemResponse]:
    items: List[Item] = db.query(Item).all()
    # return items
    return [ItemResponse.model_validate(it) for it in items]


# 7 mashgulot itemni id bo'yicha olish
@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.name is not None:
        db_item.name = item.name
    if item.description is not None:
        db_item.description = item.description
    if item.price is not None:
        db_item.price = item.price

    db.commit()
    db.refresh(db_item)
    return db_item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return None
