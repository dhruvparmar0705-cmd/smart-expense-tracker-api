# AI_NOTES.md

# AI Notes

## AI Tool Used

**Claude (Anthropic)** was used as a development assistant throughout this project. It helped generate an initial project structure, FastAPI boilerplate, endpoint implementations, and testing ideas. All AI-generated code was reviewed, executed, and refined before being included in the final submission.

---

## 1. AI-Generated vs. Manually Reviewed and Modified

AI assisted with:

* Initial FastAPI project scaffolding.
* Endpoint boilerplate for expense management.
* Pydantic model definitions.
* Initial JSON storage implementation.
* Draft versions of the pytest test suite.
* Initial drafts of the README and this document.

I manually:

* Reviewed every generated file before accepting it.
* Refactored portions of the code for readability and maintainability.
* Improved validation logic and error handling.
* Verified API behavior through manual testing.
* Expanded and refined the test suite with additional edge cases.
* Updated documentation to accurately reflect the final implementation.

Every source file was executed and tested before being included in the final project.

---

## 2. Validation, Testing, and Improvements

After generating the initial implementation, I performed several validation and refinement steps:

* Ran the complete pytest suite and fixed issues discovered during execution.
* Resolved a Pydantic model issue caused by a field name conflicting with a type annotation by updating the date import and type usage.
* Started the application using Uvicorn and manually tested the API using HTTP requests in addition to automated tests.
* Refactored the test setup so each test uses an isolated temporary JSON file, preventing shared state between tests.
* Added and verified validation rules for:

  * Positive expense amounts
  * Non-empty titles
  * Non-empty categories
* Verified filtering behavior and ensured category matching behaves consistently while preserving stored values.
* Confirmed the installation, server startup, and testing commands documented in the README work correctly from a clean project checkout.

These changes ensured the project behaves reliably beyond the initial AI-generated implementation.

---

## 3. AI Suggestions Not Used

Several AI suggestions were intentionally not adopted:

### SQLite Database

AI suggested replacing JSON storage with SQLite for more realistic persistence. I chose to keep JSON storage because it matches the assignment requirements and keeps the implementation lightweight.

### UUID-Based Expense IDs

AI proposed using UUIDs for expense identifiers. I retained sequential integer IDs because they are simpler, easier to test, and better aligned with the assignment specification.

### Global Exception Wrapper

AI suggested wrapping all endpoints with a generic exception handler. I decided against this because FastAPI already provides clear validation errors, and broad exception handling could hide useful debugging information.

### Docker Support

Docker was considered as the optional bonus feature. Instead, I chose to use FastAPI's built-in OpenAPI/Swagger documentation, which provides immediate API documentation with minimal additional complexity.

---

## 4. Reflection

AI significantly accelerated the initial implementation by generating boilerplate code and suggesting project structure. However, the final submission reflects manual review, testing, debugging, validation, and refinement. Every endpoint and test was executed, and the implementation was adjusted where necessary to improve correctness, maintainability, and alignment with the assignment requirements.
