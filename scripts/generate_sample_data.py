# scripts/generate_sample_data.py
"""
Generate sample data for FlatZ Reco Service
users.csv –  id,name,block
items.csv –  id,title,description,community,created_at
interactions.csv – id,user_id,item_id,interaction_type,timestamp
"""

import csv
import random
from datetime import datetime, timedelta, UTC
from pathlib import Path

from faker import Faker

fake = Faker()
rand = random.Random(42)                      # deterministic

OUT_DIR = Path(__file__).resolve().parent.parent
USERS_CSV = OUT_DIR / "users.csv"
ITEMS_CSV = OUT_DIR / "items.csv"
INTERACTIONS_CSV = OUT_DIR / "interactions.csv"

N_USERS = 500
N_ITEMS = 1_000
N_INTERACTIONS = 10_000

COMMUNITIES = [f"Block-{c}" for c in "ABCDEFGHIJ"]      # 10 communities
INTERACTION_TYPES = ["view", "click", "like", "book", "dismiss"]

# ---------- helpers --------------------------------------------------------- #
def random_date_within(days_back: int = 90) -> datetime:
    """Return a UTC-aware datetime within the last `days_back` days."""
    offset = rand.randint(0, days_back * 24 * 3600)
    return datetime.now(UTC) - timedelta(seconds=offset)

# ---------- generate users -------------------------------------------------- #
users = []
for uid in range(1, N_USERS + 1):
    users.append(
        {
            "id": uid,
            "name": fake.name(),
            "block": rand.choice(COMMUNITIES),
        }
    )

# ---------- generate items -------------------------------------------------- #
items = []
for iid in range(1, N_ITEMS + 1):
    community = rand.choice(COMMUNITIES)
    title_words = fake.words(nb=4, unique=True)
    items.append(
        {
            "id": iid,
            "title": " ".join(title_words).title(),
            "description": fake.sentence(nb_words=12),
            "community": community,
            "created_at": random_date_within(60).isoformat(),
        }
    )

# ---------- generate interactions ------------------------------------------ #
interactions = []
for iid in range(1, N_INTERACTIONS + 1):
    user = rand.choice(users)
    item = rand.choice(items)

    interactions.append(
        {
            "id": iid,
            "user_id": user["id"],
            "item_id": item["id"],
            "interaction_type": rand.choices(
                INTERACTION_TYPES,
                weights=[0.55, 0.25, 0.12, 0.05, 0.03],
            )[0],
            "timestamp": random_date_within(30).isoformat(),
        }
    )

# ---------- write CSV files ------------------------------------------------- #
def write_csv(path: Path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {path.relative_to(OUT_DIR)}  ({len(rows)} rows)")

write_csv(USERS_CSV, users, ["id", "name", "block"])
write_csv(ITEMS_CSV, items, ["id", "title", "description", "community", "created_at"])
write_csv(
    INTERACTIONS_CSV,
    interactions,
    ["id", "user_id", "item_id", "interaction_type", "timestamp"],
)
