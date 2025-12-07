from fastapi import FastAPI
from .database import Base, engine
from .routers import books, members, transactions, fines

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Library Management API", version="1.0")

app.include_router(books.router)
app.include_router(members.router)
app.include_router(transactions.router)
app.include_router(fines.router)

@app.get("/", tags=["Root"])
def root():
    return {"ok": True, "service": "Library Management API"}