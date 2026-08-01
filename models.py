"""Pydantic models used by the Expense Tracker API."""
import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    """Payload for creating a new expense. `id` is assigned by the server."""

    title: str = Field(..., min_length=1, description="Short description of the expense")
    amount: float = Field(..., gt=0, description="Expense amount, must be positive")
    category: str = Field(..., min_length=1, description="Category, e.g. 'food', 'travel'")
    date: dt.date = Field(..., description="Date the expense occurred (YYYY-MM-DD)")

    @field_validator("title", "category")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be blank")
        return v


class Expense(ExpenseCreate):
    """A stored expense, including its server-assigned id."""

    id: int


class TotalResponse(BaseModel):
    total: float


class CategoryTotal(BaseModel):
    category: str
    total: float


class TotalsByCategoryResponse(BaseModel):
    totals: list[CategoryTotal]
    overall_total: float
