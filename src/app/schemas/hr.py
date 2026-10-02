from pydantic import BaseModel, ConfigDict


class HRCreate(BaseModel):
    name: str
    email: str


class HRResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(
        from_attributes=True
    )