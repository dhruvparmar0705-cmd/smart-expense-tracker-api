# AI Notes

## Tool used
Claude (Anthropic), used interactively to draft the implementation and test
suite.

## 1. What was AI-generated vs. written by hand

Practically all of the initial code — `src/models.py`, `src/storage.py`,
`src/main.py`, and the full test suite in `tests/test_api.py` — was
AI-generated in a single working session, based on a plain-English
description of the requirements (add/list/filter/total/delete expenses,
JSON-file storage, FastAPI). The README and this file were also drafted by
the AI and then edited for accuracy.

Nothing here was copy-pasted blind: every file was read, run, and in several
cases corrected before being accepted (see below). No part of the codebase
was written without being executed at least once.

## 2. What was validated, tested, or changed, and why

- **Ran the full test suite before trusting it.** The first version of
  `models.py` used `from datetime import date` and then a field literally
  named `date`, which crashed Pydantic at import time
  (`PydanticUserError: ... field name clashing with a type annotation`).
  This was caught immediately by running `pytest`, not by reading the code.
  Fixed by importing the module as `datetime as dt` and typing the field as
  `dt.date` instead of shadowing the name.
- **Booted the real server and hit it with `curl`**, not just the test
  client — `POST /expenses`, `GET /expenses`, `GET /totals` — to confirm the
  API behaves the same way outside of pytest's `TestClient` (different code
  path: real ASGI server + real JSON file on disk vs. an in-process test
  client).
- **Checked the tests aren't hiding state leakage.** The AI's first instinct
  was a single module-level `ExpenseStore` reused across all tests. Changed
  this to a pytest fixture that gives every test its own `tmp_path`-backed
  JSON file, so tests can't pass or fail depending on execution order — this
  was verified by running `pytest -v` and confirming order-independent,
  isolated pass/fail per test.
- **Manually re-checked the validation rules** against the brief: amount
  must be positive (`gt=0`, rejecting both `0` and negatives), title/category
  can't be blank strings — added explicit parametrized tests for these
  edge cases rather than trusting that FastAPI's default type validation
  alone would cover them.
- **Verified the README's commands work on a clean checkout** — deleted the
  generated `data/` directory and `__pycache__`/`.pytest_cache`, then re-ran
  the exact `pip install`, `uvicorn`, and `pytest` commands from the README
  from scratch to make sure they work verbatim, since the assignment says
  they'll be run exactly as written.
- **Confirmed category filtering is case-insensitive** by design (matches
  "Food" against a filter of "food") but that original casing is preserved
  in storage — this was a deliberate choice, tested explicitly, rather than
  an accidental side effect of `.lower()` calls scattered through the code.

## 3. AI suggestions considered and not used

- **A database (SQLite) suggestion.** The AI's first draft of the plan
  suggested SQLite for "more realistic" persistence. Rejected in favor of
  the plain JSON file specified in the brief ("no database required") —
  using a DB would have added complexity (migrations, connection handling)
  the assignment explicitly doesn't ask for.
- **Auto-generated UUIDs for expense IDs.** The AI initially proposed UUIDs
  instead of incrementing integers. Rejected: the brief's example schema
  implies simple, human-readable IDs, and integer IDs are easier to
  demonstrate over `curl`/Swagger during review.
- **A generic `Exception` handler / global try-except wrapper** around every
  route "for robustness." Rejected — it would have swallowed FastAPI's
  built-in validation errors (which already return clean `422` responses)
  and made real bugs harder to see during development and testing.
- **Docker support (one of the optional bonuses).** Considered, but skipped
  in favor of Swagger/OpenAPI docs, which FastAPI provides for free and
  which seemed like better value for the time budget than writing and
  testing a Dockerfile.
