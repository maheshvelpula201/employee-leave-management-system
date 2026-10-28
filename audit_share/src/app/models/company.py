from sqlalchemy import Column, Integer, String, Text, Boolean


from src.app.db.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

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

    phone = Column(
        String,
        nullable=True
    )

    address = Column(
        Text,
        nullable=True
    )

    city = Column(
        String,
        nullable=True
    )

    state = Column(
        String,
        nullable=True
    )

    country = Column(
        String,
        nullable=True
    )

    website = Column(
        String,
        nullable=True
    )

    description = Column(
        Text,
        nullable=True
    )

    company_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=False
    )