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
    previous_last_watered = db.Column(db.DateTime, nullable=True)
    previous_snoozed_until = db.Column(db.DateTime, nullable=True)
    is_reverted = db.Column(db.Boolean, nullable=False, default=False)
    reverted_at = db.Column(db.DateTime, nullable=True)
    plant = db.relationship("Plant", backref="watering_events")

    def __repr__(self):
        return f"<WateringEvent plant_id={self.plant_id} watered_at={self.watered_at}>"


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey("species.id"), nullable=False)
    last_watered = db.Column(db.DateTime, default=datetime.utcnow)
    snoozed_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def next_watering(self):
        base_next_watering = self.last_watered + timedelta(days=self.species.watering_interval_days)
        if self.snoozed_until and self.snoozed_until > base_next_watering:
            return self.snoozed_until
        return base_next_watering

    @property
    def is_overdue(self):
        return datetime.utcnow() >= self.next_watering

    @property
    def days_until_watering(self):
        delta = self.next_watering - datetime.utcnow()
        return delta.days

    def water(self):
        self.last_watered = datetime.utcnow()
        self.snoozed_until = None

    def snooze(self, days):
        anchor = max(self.next_watering, datetime.utcnow())
        self.snoozed_until = anchor + timedelta(days=days)

    def __repr__(self):
        return f"<Plant {self.name} ({self.species.name})>"
