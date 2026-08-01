"""Simple JSON-file backed persistence for expenses.

Kept deliberately simple (no ORM/DB) per the assignment brief: data lives in
a single JSON file on disk and is read/written on every operation. This is
fine for a personal expense tracker's expected data volume and keeps the
implementation easy to reason about and test.
"""
import json
import threading
from pathlib import Path
from typing import List, Optional

from .models import Expense, ExpenseCreate

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "expenses.json"


class ExpenseStore:
    """Thread-safe CRUD store for expenses, persisted to a JSON file."""

    def __init__(self, data_file: Path = DEFAULT_DATA_FILE):
        self.data_file = Path(data_file)
        self._lock = threading.Lock()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._write([])

    # -- internal helpers ---------------------------------------------
    def _read(self) -> List[dict]:
        with open(self.data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, records: List[dict]) -> None:
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, default=str)

    def _next_id(self, records: List[dict]) -> int:
        return (max((r["id"] for r in records), default=0)) + 1

    # -- public API ------------------------------------------------------
    def add(self, expense: ExpenseCreate) -> Expense:
        with self._lock:
            records = self._read()
            new_id = self._next_id(records)
            record = {"id": new_id, **json.loads(expense.model_dump_json())}
            records.append(record)
            self._write(records)
            return Expense(**record)

    def list_all(self) -> List[Expense]:
        with self._lock:
            records = self._read()
        return [Expense(**r) for r in records]

    def filter_by_category(self, category: str) -> List[Expense]:
        return [
            e for e in self.list_all()
            if e.category.strip().lower() == category.strip().lower()
        ]

    def get(self, expense_id: int) -> Optional[Expense]:
        for e in self.list_all():
            if e.id == expense_id:
                return e
        return None

    def delete(self, expense_id: int) -> bool:
        with self._lock:
            records = self._read()
            filtered = [r for r in records if r["id"] != expense_id]
            if len(filtered) == len(records):
                return False
            self._write(filtered)
            return True

    def total(self) -> float:
        return round(sum(e.amount for e in self.list_all()), 2)

    def totals_by_category(self) -> dict:
        totals: dict = {}
        for e in self.list_all():
            totals[e.category] = round(totals.get(e.category, 0) + e.amount, 2)
        return totals

    def clear(self) -> None:
        with self._lock:
            self._write([])
