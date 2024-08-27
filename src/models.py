from pydantic import BaseModel, Field
from bson.objectid import ObjectId as _ObjectId
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated, Optional

def check_object_id(value: str) -> str:
    if not _ObjectId.is_valid(value):
        raise ValueError('Invalid ObjectId')
    return value


PyObjectId = Annotated[str, BeforeValidator(str)]

class Book(BaseModel):
    id: Optional[PyObjectId] = Field(alias = "_id", default=None)
    title: str = Field(...)
    author: str = Field(...)
    month: int = Field(...)
    year: int = Field(...)
    pages: int = Field(...)
    rating: int = Field(...)
    status: str = Field(...)
    category: str = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed=True,
        json_schema_extra = {
            "example": {
                "_id": "66cddf75b9691bdae9824eac",
                "title": "The Dinner",
                "author": "Koch Herman",
                "month": 8,
                "year": 2024,
                "pages": 267,
                "rating": 4,
                "status": "completed",
                "category": "crime"
            }
        }