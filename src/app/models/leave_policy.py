from sqlalchemy import Column, Integer, String

from src.app.db.database import Base


class LeavePolicy(Base):
    __tablename__ = "leave_policies"

    id = Column(Integer, primary_key=True, index=True)

    leave_type = Column(String, nullable=False)

    annual_days = Column(Integer, nullable=False)

    year = Column(Integer, nullable=False)