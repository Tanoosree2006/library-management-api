# State Machine Explanation

## Book
States: `available`, `borrowed`, `reserved`, `maintenance`

Transitions implemented in this MVP:
- `available -> borrowed` (when a transaction is opened via borrow endpoint)
- `borrowed -> available` (when a transaction is returned)
- Note: `reserved` and `maintenance` exist in the schema but do not have dedicated endpoints in this MVP.

## Transaction
States: `open`, `overdue`, `returned`

- On borrow: create transaction with `status=open`, `borrowed_at=now`, `due_at=now+14d`.
- Overdue recalculation:
  - If `status != returned` and `due_at < now`, set `status=overdue`.
  - Triggered by `GET /transactions/overdue` or `POST /fines/recalculate`.
- On return:
  - Set `returned_at=now`.
  - If `returned_at > due_at`, create a Fine (`overdue_days * 0.50`).
  - Set `status=returned`.

## Member
States: `active`, `suspended`, `closed`

- Member starts as `active`.
- After recalculation or returns, if member has `>= 3` overdue transactions → `suspended`.
- If member has 0 overdue transactions **and** no unpaid fines → set back to `active`.

## Enforcement points
- Borrowing checks: member active, no unpaid fines, <3 open borrows, book available.
- Return applies fines and frees book.
- Recalculation ensures data consistency over time.