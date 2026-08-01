"""Tests for the Smart Expense Tracker API.

Each test gets a fresh, isolated JSON data file (via a pytest fixture that
overrides the app's storage instance), so tests never depend on each other
or on any pre-existing data.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from src import main
from src.storage import ExpenseStore


@pytest.fixture()
def client(tmp_path):
    """Provide a TestClient backed by a fresh, temp-file-based store."""
    test_store = ExpenseStore(data_file=tmp_path / "expenses_test.json")
    main.store = test_store  # swap out the module-level store used by routes
    return TestClient(main.app)


def make_expense(**overrides):
    payload = {
        "title": "Coffee",
        "amount": 4.5,
        "category": "food",
        "date": "2026-07-01",
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------
# Add expense
# ---------------------------------------------------------------------

def test_add_expense_returns_created_expense_with_id(client):
    resp = client.post("/expenses", json=make_expense())
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["title"] == "Coffee"
    assert body["amount"] == 4.5
    assert body["category"] == "food"
    assert body["date"] == "2026-07-01"


def test_add_expense_ids_increment(client):
    client.post("/expenses", json=make_expense(title="A"))
    resp = client.post("/expenses", json=make_expense(title="B"))
    assert resp.json()["id"] == 2


@pytest.mark.parametrize(
    "bad_field,bad_value",
    [
        ("amount", -5),
        ("amount", 0),
        ("title", ""),
        ("category", ""),
    ],
)
def test_add_expense_rejects_invalid_data(client, bad_field, bad_value):
    resp = client.post("/expenses", json=make_expense(**{bad_field: bad_value}))
    assert resp.status_code == 422


def test_add_expense_rejects_missing_fields(client):
    resp = client.post("/expenses", json={"title": "Coffee"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------
# List / view all
# ---------------------------------------------------------------------

def test_list_expenses_empty_initially(client):
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_expenses_returns_all_added(client):
    client.post("/expenses", json=make_expense(title="Coffee"))
    client.post("/expenses", json=make_expense(title="Bus ticket", category="travel"))
    resp = client.get("/expenses")
    assert resp.status_code == 200
    titles = {e["title"] for e in resp.json()}
    assert titles == {"Coffee", "Bus ticket"}


def test_get_single_expense_by_id(client):
    created = client.post("/expenses", json=make_expense()).json()
    resp = client.get(f"/expenses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Coffee"


def test_get_single_expense_404_when_missing(client):
    resp = client.get("/expenses/999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------
# Filter by category
# ---------------------------------------------------------------------

def test_filter_by_category_query_param(client):
    client.post("/expenses", json=make_expense(title="Coffee", category="food"))
    client.post("/expenses", json=make_expense(title="Taxi", category="travel"))
    resp = client.get("/expenses", params={"category": "food"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Coffee"


def test_filter_by_category_is_case_insensitive(client):
    client.post("/expenses", json=make_expense(title="Coffee", category="Food"))
    resp = client.get("/expenses", params={"category": "food"})
    assert len(resp.json()) == 1


def test_filter_by_category_path_endpoint(client):
    client.post("/expenses", json=make_expense(title="Coffee", category="food"))
    client.post("/expenses", json=make_expense(title="Taxi", category="travel"))
    resp = client.get("/expenses/category/travel")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Taxi"


def test_filter_by_category_no_matches_returns_empty_list(client):
    client.post("/expenses", json=make_expense(category="food"))
    resp = client.get("/expenses", params={"category": "entertainment"})
    assert resp.status_code == 200
    assert resp.json() == []


# ---------------------------------------------------------------------
# Totals
# ---------------------------------------------------------------------

def test_total_is_zero_when_no_expenses(client):
    resp = client.get("/totals")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_total_sums_all_expenses(client):
    client.post("/expenses", json=make_expense(amount=10))
    client.post("/expenses", json=make_expense(amount=15.5))
    resp = client.get("/totals")
    assert resp.json()["total"] == 25.5


def test_totals_by_category(client):
    client.post("/expenses", json=make_expense(amount=10, category="food"))
    client.post("/expenses", json=make_expense(amount=5, category="food"))
    client.post("/expenses", json=make_expense(amount=20, category="travel"))
    resp = client.get("/totals/by-category")
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_total"] == 35
    totals = {t["category"]: t["total"] for t in body["totals"]}
    assert totals == {"food": 15, "travel": 20}


# ---------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------

def test_delete_expense_removes_it(client):
    created = client.post("/expenses", json=make_expense()).json()
    resp = client.delete(f"/expenses/{created['id']}")
    assert resp.status_code == 204
    resp = client.get(f"/expenses/{created['id']}")
    assert resp.status_code == 404


def test_delete_nonexistent_expense_returns_404(client):
    resp = client.delete("/expenses/12345")
    assert resp.status_code == 404


def test_delete_then_totals_update(client):
    e1 = client.post("/expenses", json=make_expense(amount=10)).json()
    client.post("/expenses", json=make_expense(amount=5))
    client.delete(f"/expenses/{e1['id']}")
    resp = client.get("/totals")
    assert resp.json()["total"] == 5


# ---------------------------------------------------------------------
# Persistence sanity check
# ---------------------------------------------------------------------

def test_store_persists_to_disk_across_instances(tmp_path):
    data_file = tmp_path / "persist_test.json"
    from src.models import ExpenseCreate

    store1 = ExpenseStore(data_file=data_file)
    store1.add(ExpenseCreate(**make_expense()))

    store2 = ExpenseStore(data_file=data_file)
    assert len(store2.list_all()) == 1
