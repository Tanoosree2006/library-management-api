from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

books = [
    models.Book(title="Clean Code", author="Robert C. Martin", category="Software"),
    models.Book(title="Deep Work", author="Cal Newport", category="Productivity"),
    models.Book(title="The Pragmatic Programmer", author="Andrew Hunt", category="Software"),
]
members = [
    models.Member(name="Alice", email="alice@example.com"),
    models.Member(name="Bob", email="bob@example.com"),
]

db.add_all(books + members)
db.commit()
db.close()
print("Seeded 3 books + 2 members")