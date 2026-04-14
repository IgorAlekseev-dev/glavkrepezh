from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class PriceDoc(Base):
    __tablename__ = "price_docs"
    id: Mapped[int] = mapped_column(primary_key=True)