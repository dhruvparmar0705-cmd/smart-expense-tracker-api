"""Smart Expense Tracker API.

A small REST API for tracking personal expenses: add, list, filter by
category, delete, and compute totals (overall and per-category).
"""
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from .models import (
    CategoryTotal,
    Expense,
    ExpenseCreate,
    TotalResponse,
    TotalsByCategoryResponse,
)
from .storage import ExpenseStore

app = FastAPI(
    title="Smart Expense Tracker API",
    description="A simple REST API to manage personal expenses.",
    version="1.0.0",
)

store = ExpenseStore()


@app.get("/", tags=["health"])
def root():
    """Basic health-check / welcome endpoint."""
    return {"message": "Smart Expense Tracker API is running", "docs": "/docs"}


@app.post("/expenses", response_model=Expense, status_code=201, tags=["expenses"])
def add_expense(expense: ExpenseCreate):
    """Add a new expense."""
    return store.add(expense)


@app.get("/expenses", response_model=List[Expense], tags=["expenses"])
def list_expenses(
    category: Optional[str] = Query(
        None, description="Filter results by category (case-insensitive)"
    )
):
    """View all expenses, optionally filtered by category."""
    if category:
        return store.filter_by_category(category)
    return store.list_all()


@app.get("/expenses/{expense_id}", response_model=Expense, tags=["expenses"])
def get_expense(expense_id: int):
    """Fetch a single expense by id."""
    expense = store.get(expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return expense


@app.delete("/expenses/{expense_id}", status_code=204, tags=["expenses"])
def delete_expense(expense_id: int):
    """Delete an expense by id."""
    deleted = store.delete(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")
    return JSONResponse(status_code=204, content=None)


@app.get("/expenses/category/{category}", response_model=List[Expense], tags=["expenses"])
def get_expenses_by_category(category: str):
    """Explicit path-based filter by category (alternative to the query param)."""
    return store.filter_by_category(category)


@app.get("/totals", response_model=TotalResponse, tags=["totals"])
def get_total():
    """Total of all expenses."""
    return TotalResponse(total=store.total())


@app.get("/totals/by-category", response_model=TotalsByCategoryResponse, tags=["totals"])
def get_totals_by_category():
    """Totals broken down by category, plus the overall total."""
    totals = store.totals_by_category()
    return TotalsByCategoryResponse(
        totals=[CategoryTotal(category=c, total=t) for c, t in totals.items()],
        overall_total=round(sum(totals.values()), 2),
    )
