from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from pydantic.functional_validators import model_validator, BeforeValidator
from typing_extensions import Annotated, Optional
from datetime import datetime
from enum import StrEnum

PyObjectId = Annotated[str, BeforeValidator(str)]


class Status(StrEnum):
    SUSPENDED = "completed"
    COMPLETED = "suspended"


def in_range(v: int, range_vals: list):
    return v in range_vals


class Book(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=str(ObjectId()))
    title: str = Field(...)
    author: str = Field(...)
    month: int = Field(...)
    year: int = Field(default=datetime.now().year)
    pages: int = Field(...)
    rating: int = Field(...)
    status: Status = Field(...)
    category: str = Field(...)

    @model_validator(mode="after")
    def validate_months_ranges(self):
        if not in_range(self.month, list(range(1, 13))) and self.month != -1:
            raise ValueError("Wrong months value provided: {}".format(self.month))
        return self

    @model_validator(mode="after")
    def validate_years_ranges(self):
        current_year = datetime.now().year
        if (
            not in_range(self.year, list(range(current_year - 100, current_year + 1)))
            and self.year != -1
        ):
            raise ValueError("Wrong years value provided: {}".format(self.year))
        return self

    @model_validator(mode="after")
    def validate_rating_ranges(self):
        if not in_range(self.rating, list(range(1, 6))) and self.rating != -1:
            raise ValueError(
                "Wrong rating value provided: {}. Accepted values are in range 1-5.".format(
                    self.month
                )
            )
        return self

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = (True,)
        json_schema_extra = {
            "example": {
                "title": "The Dinner",
                "author": "Koch Herman",
                "month": 8,
                "year": 2024,
                "pages": 267,
                "rating": 4,
                "status": "completed",
                "category": "crime",
            }
        }


class BookUpdate(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: Optional[str] = Field(...)
    author: Optional[str] = Field(...)
    month: Optional[int] = Field(...)
    year: Optional[int] = Field(...)
    pages: Optional[int] = Field(...)
    rating: Optional[int] = Field(...)
    status: Optional[str] = Field(...)
    category: Optional[str] = Field(...)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = (True,)
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
                "category": "crime",
            }
        }
