# API Documentation (Detailed)

Base URL: `http://127.0.0.1:8000`

## Books
### GET /books
- 200 OK → list of books

### POST /books
- Body:
```json
{ "title": "Clean Architecture", "author": "Robert C. Martin", "category": "Software" }
```
- 201 Created → created book

### GET /books/{id}
- 200 OK → book or 404

### PUT /books/{id}
- Body same as create
- 200 OK → updated

### DELETE /books/{id}
- 204 No Content

### GET /books/available/list
- 200 OK → list of `status=available`

## Members
### GET /members
### POST /members
```json
{ "name": "Alice", "email": "alice@example.com" }
```
- 201 Created

### GET /members/{id}
### PUT /members/{id}
```json
{ "name": "Alice Updated", "email": "alice.updated@example.com" }
```

### DELETE /members/{id}
- 204

### GET /members/{id}/books
- 200 OK → books currently borrowed (non-returned)

### GET /members/{id}/transactions
- 200 OK → all transactions for member

## Transactions
### POST /transactions/borrow?book_id={id}&member_id={id}
- 201 Created → transaction
- 400 if:
  - book not available
  - member has unpaid fines
  - member not active
  - member has >= 3 open borrows

### POST /transactions/{id}/return
- 200 OK → returned transaction
- Fine auto-created if overdue

### GET /transactions/overdue
- 200 OK → list of overdue transactions (also recalculates status)

## Fines
### GET /fines
- 200 OK → list of fines

### POST /fines/recalculate
- 200 OK → `{ "updated_transactions": N }`

### POST /fines/{id}/pay
- Body:
```json
{ "amount": 2.50 }
```
- 200 OK → fine with `status=paid` (this MVP expects full amount)