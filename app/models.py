from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# class Base(DeclarativeBase):
#     pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        "password", String(255), nullable=False
    )
    # password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user", server_default="user"
    )
    # role: Mapped[str] = mapped_column(String(20), default="user")

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    # обратная связь — доступ ко всем товарам категории
    # items = relationship("Item", back_populates="category")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )  # уникальный идентификатор товара
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # название товара
    description: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # описание товара
    price: Mapped[int] = mapped_column(Integer, nullable=False)  # цена в копейках

    # Связь с категорией (1 → N)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", name="fk_items_category_id"),
        nullable=True,
        index=True,
    )  # ссылка на категорию товара

    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="items",
        lazy="joined",
    )  # обратная связь — доступ к категории товара
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", name="fk_items_owner_id"),
        nullable=False,
        index=True,
    )  # ссылка на владельца товара
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="items",
        lazy="joined",
    )  # обратная связь — доступ к владельцу товара


image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)


def __repr__(self) -> str:
    return f"<Item(id={self.id}, name={self.name!r}, price={self.price}, owner_id={self.owner_id})>"
