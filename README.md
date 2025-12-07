# Library Management REST API (FastAPI + SQLite)

This project implements a RESTful API for a library management system that handles **books**, **members**, **borrowing transactions**, and **fines**. It includes state-machine style transitions for book and member statuses and enforces the core business rules defined in the assignment.

---

## 1) Setup & Run

### Prerequisites
- Python 3.10+
- pip

### Steps
```bash
# clone
git clone <your-repo-url>.git
cd library_api

# create & activate venv (Windows)
python -m venv .venv
.\.venv\Scriptsctivate

# macOS/Linux
# python3 -m venv .venv
# source .venv/bin/activate

# install deps
pip install -r requirements.txt

# optional: seed data
python seed.py

# run
uvicorn app.main:app --reload
```
Open docs: http://127.0.0.1:8000/docs

---

## 2) API Overview

- **Books**: CRUD + `GET /books/available/list`
- **Members**: CRUD + `GET /members/{id}/books`, `GET /members/{id}/transactions`
- **Transactions**: `POST /transactions/borrow?book_id=&member_id=`, `POST /transactions/{id}/return`, `GET /transactions/overdue`
- **Fines**: `GET /fines`, `POST /fines/recalculate`, `POST /fines/{id}/pay`

Full request/response examples are in [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md).

---

## 3) Database Schema

- SQLite + SQLAlchemy ORM
- Entities: **Book**, **Member**, **Transaction**, **Fine**
- Timestamps stored in UTC

Diagram (Mermaid):

```mermaid
erDiagram
  BOOK ||--o{ TRANSACTION : "book_id"
  MEMBER ||--o{ TRANSACTION : "member_id"
  MEMBER ||--o{ FINE : "member_id"
  TRANSACTION ||--o{ FINE : "transaction_id"

  BOOK {
    int id PK
    string title
    string author
    string category
    enum status (available|borrowed|reserved|maintenance)
    datetime created_at
    datetime updated_at
  }

  MEMBER {
    int id PK
    string name
    string email (unique)
    enum status (active|suspended|closed)
    float total_fines_due
    datetime created_at
    datetime updated_at
  }

  TRANSACTION {
    int id PK
    int book_id FK -> BOOK.id
    int member_id FK -> MEMBER.id
    enum status (open|overdue|returned)
    datetime borrowed_at
    datetime due_at
    datetime returned_at (nullable)
    datetime created_at
    datetime updated_at
  }

  FINE {
    int id PK
    int member_id FK -> MEMBER.id
    int transaction_id FK -> TRANSACTION.id (nullable)
    float amount
    string reason
    string status (unpaid|paid)
    datetime created_at
    datetime updated_at
  }
```

---

## 4) State Machine & Business Rules

### Book status transitions
- `available -> borrowed` (on borrow)
- `borrowed -> available` (on return)
- `open/overdue` tracked on Transaction; `overdue` is recalculated if `due_at` < now
- Reserved/Maintenance are present as statuses but not exposed by endpoints in this MVP

### Member status transitions
- Start as `active`
- Auto-**suspended** when member has **3+ overdue** transactions
- Auto-**active** when overdue count returns to 0 **and** there are no unpaid fines

### Borrow rules
- Max **3** concurrent borrows per member
- Loan period **14 days**
- Member must be **active** and have **no unpaid fines**
- Book must be **available**

### Return & Fine calculation
- On return, if `returned_at > due_at`, create a Fine:
  - **fine = overdue_days × $0.50**
  - Add to `member.total_fines_due`

### Fine payment
- `POST /fines/{id}/pay` marks the fine as `paid` and reduces `member.total_fines_due`

Implementation details in [`app/service.py`](app/service.py).

---

## 5) Postman / HTTP Client
- Postman files in repository root:
  - `Library Management API (FastAPI + SQLite).postman_collection.json`
  - `Library API Local.postman_environment.json`
- VS Code REST Client file: [`docs/requests.http`](docs/requests.http)

---

## 6) Error Handling & Status Codes
- 404 for not found resources
- 400 for business rule violations (e.g., borrowing limit, unpaid fines, wrong status)
- 201 on successful creates
- 204 on delete

---

## 7) Project structure
```
app/
  main.py
  database.py
  models.py
  schemas.py
  service.py
  routers/
    books.py
    members.py
    transactions.py
    fines.py
docs/
  API_DOCUMENTATION.md
  requests.http
README.md
requirements.txt
seed.py
```

---

## 8) How to run tests (manual)
Use Postman collection or VS Code REST Client (`docs/requests.http`). Test scenarios listed in `docs/API_DOCUMENTATION.md`.# library-management-api
