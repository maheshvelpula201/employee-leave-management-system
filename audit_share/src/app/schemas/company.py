from pydantic import BaseModel


class CompanyStatusUpdate(BaseModel):

    status: str