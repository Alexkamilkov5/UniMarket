from pathlib import Path
from typing import List  # stdlib (оставьте только если реально используете)
from typing import Optional, Sequence, cast

# import uvicorn
from fastapi import Query  # third-party
from fastapi import Depends, FastAPI, File, HTTPException, Security, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password  # first-party
from app.config import settings
from app.deps import get_db
from app.middleware import RequestLoggingMiddleware
from app.models import Category, Item, User
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    ItemCreate,
    ItemResponse,
    ItemUpdate,
    PageItems,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)

SECRET_KEY = settings.UNIMARKET_SECRET_KEY
ALGORITHM = settings.ALGORITHM
# from app.database import get_db

# Login endpoint -login uchun endpoint

# Endpoint to get current user info 7 punkt

# app = FastAPI(title="UniMarket", version="0.1.0")
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Musayev-Платформа для покупки и продажи товаров между студентами",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,  # Используем из настроек
)

app.add_middleware(
    RequestLoggingMiddleware
)  # Добавляем наше middleware для логирования запросов
app.mount("/uploads", StaticFiles(directory="app/static"), name="uploads")


# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="fronted"), name="static")


# @app.get("/")
# async def root():
# return {"message": "UniMarket API работает!", "status": "ok"}
@app.get("/", response_class=HTMLResponse)
def read_index():
    return Path("fronted/index.html").read_text(encoding="utf-8")


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

    new_user = User(
        username=request.username, hashed_password=hash_password(request.password)
    )
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
    if not user or not verify_password(
        form_data.password, user.hashed_password  # type: ignore[arg-type]
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username})
    return TokenResponse(access_token=token)


# Добавим тестовый защищённый маршрут:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


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
# @app.post("/items", response_model=ItemResponse)
# def create_item(
#     item: ItemCreate,
#     db: Session = Depends(get_db),
#     current_username: str = Depends(get_current_username),  # убери если без токена
# ) -> ItemResponse:
#     db_item = Item(name=item.name, description=item.description, price=item.price)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return ItemResponse.model_validate(db_item)


@app.post("/items")
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# Белый список допустимых полей сортировки
ALLOWED_SORT_FIELDS = {
    "id": Item.id,
    "name": Item.name,
    "price": Item.price,
}


@app.get("/items", response_model=PageItems)
def list_items(
    category_id: Optional[int] = Query(None, description="Фильтр по категории"),
    limit: int = Query(10, ge=1, le=100, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
    sort_by: str = Query(
        "id", description=f"Поле сортировки: {', '.join(ALLOWED_SORT_FIELDS.keys())}"
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Порядок: asc|desc"),
    db: Session = Depends(get_db),
) -> PageItems:
    # Базовый запрос
    q = db.query(Item)
    if category_id is not None:
        q = q.filter(Item.category_id == category_id)
    # total до пагинации
    total = q.count()
    # сортировка через белый список
    sort_col = ALLOWED_SORT_FIELDS.get(sort_by)
    if sort_col is None:
        raise HTTPException(status_code=400, detail=f"Unsupported sort_by={sort_by}")
    q = q.order_by(asc(sort_col) if order == "asc" else desc(sort_col))
    # пагинация
    items: Sequence[Item] = q.offset(offset).limit(limit).all()
    # next_offset (если есть следующая страница)
    next_offset: Optional[int] = offset + limit if offset + limit < total else None
    return PageItems(
        items=items,  # FastAPI+Pydantic v2 сам преобразует ORM → ItemResponse
        total=total,
        limit=limit,
        offset=offset,
        next_offset=next_offset,
    )


# 7 mashgulot itemni id bo'yicha olish
@app.put(
    "/items/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK
)
def update_item_clean(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    # Проверяем существование
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Получаем только заполненные поля
    update_data = item.model_dump(exclude_unset=True)

    if update_data:  # Если есть что обновлять
        stmt = sql_update(Item).where(Item.id == item_id).values(**update_data)
        db.execute(stmt)
        db.commit()
        db.refresh(db_item)

    return db_item


@app.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Проверка прав
    if db_item.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403, detail="Нельзя удалять чужие товары (только админ может)"
        )

    db.delete(db_item)
    db.commit()
    return {"ok": True, "deleted": item_id}


# 5 hafta uchun categorylar uchun endpointlar
@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@app.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


@app.post("/{item_id}/upload-image")
async def upload_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    item = db.get(Item, item_id)
    if item.owner_id != user.id and user.role != "admin":
        raise HTTPException(403, "Forbidden")
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(400, "Invalid file type")
    path = f"app/static/items/{item_id}.{ext}"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(await file.read())
    item.image_url = f"/static/items/{item_id}.{ext}"
    db.commit()
    return {"status": "ok", "url": item.image_url}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на учебном проекте можно *, в проде — домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
