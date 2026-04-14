from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    slug: Mapped[str] = mapped_column(String, index=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category", cascade="all, delete-orphan")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side=[id])

    def __repr__(self):
        return f"<Category {self.name}>"
    
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10,2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Products {self.name} - {self.price}>"