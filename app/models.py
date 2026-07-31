from datetime import datetime, timedelta

from app import db


class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    watering_interval_days = db.Column(db.Integer, nullable=False)
    plants = db.relationship("Plant", backref="species", lazy=True)

    def __repr__(self):
        return f"<Species {self.name} (every {self.watering_interval_days} days)>"


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"), nullable=False)
    last_watered = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def next_watering(self):
        return self.last_watered + timedelta(days=self.species.watering_interval_days)

    @property
    def is_overdue(self):
        return datetime.utcnow() >= self.next_watering

    @property
    def days_until_watering(self):
        delta = self.next_watering - datetime.utcnow()
        return delta.days

    def water(self):
        self.last_watered = datetime.utcnow()

    def __repr__(self):
        return f"<Plant {self.name} ({self.species.name})>"
