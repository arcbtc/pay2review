# Data models for your extension

from sqlite3 import Row
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request


from urllib.parse import urlparse

# Main table model

class CreateP2RData(BaseModel):
    wallet: Optional[str]
    price: Optional[int]
    name: Optional[str]
    total: Optional[int]
    description: Optional[str]
    review_length: Optional[int]


class P2R(BaseModel):
    id: str
    wallet: Optional[str]
    price: Optional[int]
    name: Optional[str]
    total: Optional[int]
    description: Optional[str]
    review_length: Optional[int]

    @classmethod
    def from_row(cls, row: Row) -> "P2R":
        return cls(**dict(row))

# Review model

class CreateReviewData(BaseModel):
    item_id: Optional[str]
    p2r_id: Optional[str]
    previous_id: Optional[str]
    name: Optional[str]
    review_int: Optional[int]
    review_text: Optional[str]

class Review(BaseModel):
    id: str
    item_id: Optional[str]
    p2r_id: Optional[str]
    previous_id: Optional[str]
    name: Optional[str]
    review_int: Optional[int]
    review_text: Optional[str]
    review_date: Optional[str]
    paid: Optional[bool]

    @classmethod
    def from_row(cls, row: Row) -> "P2R":
        return cls(**dict(row))