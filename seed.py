"""Seed the database with common houseplant species."""

from app import create_app, db
from app.models import Species

COMMON_SPECIES = [
    ("Pothos", 7),
    ("Snake Plant", 14),
    ("Monstera", 7),
    ("Fiddle Leaf Fig", 10),
    ("Spider Plant", 7),
    ("Peace Lily", 5),
    ("Succulent", 14),
    ("Cactus", 21),
    ("Fern", 3),
    ("Rubber Plant", 10),
]

app = create_app()

with app.app_context():
    for name, interval in COMMON_SPECIES:
        if not Species.query.filter_by(name=name).first():
            db.session.add(Species(name=name, watering_interval_days=interval))
    db.session.commit()
    print(f"Seeded {len(COMMON_SPECIES)} species.")
