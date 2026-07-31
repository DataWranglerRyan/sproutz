from datetime import datetime, timedelta

from app import db


class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    watering_interval_days = db.Column(db.Integer, nullable=False)
    sunlight = db.Column(db.String(100))
    soil_type = db.Column(db.String(200))
    common_issues = db.Column(db.Text)
    care_tips = db.Column(db.Text)
    fertilizer_type = db.Column(db.String(200))
    fertilizer_schedule = db.Column(db.String(200))
    fertilizer_notes = db.Column(db.Text)
    plants = db.relationship("Plant", backref="species", lazy=True)
    issues = db.relationship("SpeciesIssue", backref="species", lazy=True)


class SpeciesIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"), nullable=False)
    issue = db.Column(db.String(200), nullable=False)
    solution = db.Column(db.Text, nullable=False)


class WateringEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False)
    watered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    plant = db.relationship("Plant", backref="watering_events")

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
