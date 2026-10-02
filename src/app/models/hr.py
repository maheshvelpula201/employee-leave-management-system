from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.app.db.database import Base


class HR(Base):
    __tablename__ = "hrs"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    employees = relationship(
        "Employee",
        back_populates="hr"
    )