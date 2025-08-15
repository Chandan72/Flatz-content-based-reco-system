import csv
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, engine
from app.core.models import Base, User, Item, Interaction

# Ensure tables are created before loading data
Base.metadata.create_all(bind=engine)

def load_users(db: Session, path: str):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            user = User(
                id=int(row["id"]),
                name=row["name"],
                block=row["block"]
            )
            db.merge(user)  # upsert by primary key
    db.commit()

def load_items(db: Session, path: str):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            created_at = None
            if row.get("created_at"):
                created_at = datetime.fromisoformat(row["created_at"])
            item = Item(
                id=int(row["id"]),
                title=row["title"],
                description=row.get("description", ""),
                community=row["community"],
                created_at=created_at
            )
            db.merge(item)
    db.commit()

def load_interactions(db: Session, path: str):
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            timestamp = None
            if row.get("timestamp"):
                timestamp = datetime.fromisoformat(row["timestamp"])
            interaction = Interaction(
                id=int(row["id"]),
                user_id=int(row["user_id"]),
                item_id=int(row["item_id"]),
                interaction_type=row["interaction_type"],
                timestamp=timestamp
            )
            db.merge(interaction)
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Loading users...")
        load_users(db, "data/users.csv")
        print("Loading items...")
        load_items(db, "data/items.csv")
        print("Loading interactions...")
        load_interactions(db, "data/interactions.csv")
        print("Data loaded successfully.")
    finally:
        db.close()
