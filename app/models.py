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
    password: Mapped[str] = mapped_column(String, nullable=False)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    # обратная связь — доступ ко всем товарам категории
    # items = relationship("Item", back_populates="category")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="category")


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", name="fk_items_category_id"),
        nullable=True,
        index=True,
    )

    # category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    # связь с категорией
    # category = relationship("Category", back_populates="items")
    category: Mapped[Optional["Category"]] = relationship(
        "Category", back_populates="items"
    )
