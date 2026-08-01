# Smart Expense Tracker API

A REST API for tracking personal expenses — add, list, filter by category,
delete, and compute totals (overall and per-category). Built with **Python
+ FastAPI**, data persisted to a local JSON file (no database required).

## What was built

- `POST /expenses` — add an expense (`title`, `amount`, `category`, `date`)
- `GET /expenses` — list all expenses (optional `?category=` filter)
- `GET /expenses/{id}` — fetch a single expense
- `GET /expenses/category/{category}` — filter by category (path variant)
- `DELETE /expenses/{id}` — delete an expense
- `GET /totals` — overall total of all expenses
- `GET /totals/by-category` — totals broken down by category
- Interactive API docs auto-generated at `/docs` (Swagger UI) and `/redoc`
  courtesy of FastAPI — this covers the optional "OpenAPI/Swagger docs" bonus.

Data is stored in `data/expenses.json`, created automatically on first run.
The file is recreated fresh if deleted, so a clean checkout always starts
with zero expenses.

## Requirements

- Python 3.10+

## Install

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn src.main:app --reload
```

The API is then available at `http://127.0.0.1:8000`.
Interactive docs: `http://127.0.0.1:8000/docs`

## Run the tests

```bash
pytest tests/ -v
```

Tests use an isolated temporary JSON file per test (via a pytest `tmp_path`
fixture), so running the test suite never touches `data/expenses.json` and
tests don't leak state into each other.

## Example usage

```bash
# Add an expense
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Lunch", "amount": 12.5, "category": "food", "date": "2026-07-30"}'

# List all expenses
curl http://127.0.0.1:8000/expenses

# Filter by category
curl "http://127.0.0.1:8000/expenses?category=food"

# Overall total
curl http://127.0.0.1:8000/totals

# Totals by category
curl http://127.0.0.1:8000/totals/by-category

# Delete an expense
curl -X DELETE http://127.0.0.1:8000/expenses/1
```

## Project structure

```
your-repo/
  README.md
  AI_NOTES.md
  requirements.txt
  src/
    __init__.py
    main.py       # FastAPI app and route definitions
    models.py      # Pydantic request/response models
    storage.py      # JSON-file backed persistence layer
  tests/
    __init__.py
    test_api.py     # 22 tests covering all endpoints and edge cases
```

## Design notes

- **Validation**: `amount` must be > 0, `title`/`category` can't be blank;
  FastAPI returns `422` with details on invalid input.
- **IDs**: auto-incremented server-side, so clients never set them.
- **Category matching** is case-insensitive on filtering (`Food` and `food`
  match), but the original casing is preserved on storage/display.
- **Concurrency**: a simple `threading.Lock` guards reads/writes to the JSON
  file, since FastAPI can serve requests concurrently even with in-process
  storage.
