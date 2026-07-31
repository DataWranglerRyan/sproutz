from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta

from app import db
from app.models import Plant, Species, WateringEvent

main = Blueprint("main", __name__)


@main.route("/")
def index():
    plants = Plant.query.all()
    plants_sorted = sorted(plants, key=lambda p: p.next_watering)
    return render_template("index.html", plants=plants_sorted)


@main.route("/plants/add", methods=["GET", "POST"])
def add_plant():
    if request.method == "POST":
        name = request.form["name"]
        species_id = request.form["species_id"]
        plant = Plant(name=name, species_id=species_id)
        db.session.add(plant)
        db.session.commit()
        flash(f"Added {name}!", "success")
        return redirect(url_for("main.index"))
    species = Species.query.all()
    return render_template("add_plant.html", species=species)


@main.route("/plants/<int:plant_id>/water", methods=["POST"])
def water_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    plant.water()
    event = WateringEvent(plant_id=plant.id, watered_at=datetime.utcnow())
    db.session.add(event)
    db.session.commit()
    flash(f"Watered {plant.name}!", "success")
    return redirect(url_for("main.index"))


@main.route("/plants/<int:plant_id>/delete", methods=["POST"])
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    db.session.delete(plant)
    db.session.commit()
    flash(f"Removed {plant.name}.", "info")
    return redirect(url_for("main.index"))


@main.route("/species", methods=["GET", "POST"])
def manage_species():
    if request.method == "POST":
        name = request.form["name"]
        interval = int(request.form["watering_interval_days"])
        sunlight = request.form.get("sunlight", "")
        soil_type = request.form.get("soil_type", "")
        common_issues = request.form.get("common_issues", "")
        care_tips = request.form.get("care_tips", "")
        species = Species(
            name=name,
            watering_interval_days=interval,
            sunlight=sunlight,
            soil_type=soil_type,
            common_issues=common_issues,
            care_tips=care_tips,
        )
        db.session.add(species)
        db.session.flush()  # get species.id before adding issues

        # Add issue/solution pairs
        issues = request.form.getlist("issue[]")
        solutions = request.form.getlist("solution[]")
        for issue, solution in zip(issues, solutions):
            if issue.strip() and solution.strip():
                from app.models import SpeciesIssue
                db.session.add(SpeciesIssue(
                    species_id=species.id,
                    issue=issue.strip(),
                    solution=solution.strip(),
                ))

        db.session.commit()
        flash(f"Added species: {name}", "success")
        return redirect(url_for("main.manage_species"))
    species = Species.query.all()
    return render_template("species.html", species=species)


@main.route("/species/<int:species_id>")
def species_detail(species_id):
    species = Species.query.get_or_404(species_id)
    return render_template("species_detail.html", species=species)


@main.route("/dashboard")
def dashboard():
    plants = Plant.query.all()
    today = datetime.utcnow().date()

    # Build timeline: past watering events + future scheduled waterings
    timeline_events = []

    for plant in plants:
        # Past watering events
        for event in plant.watering_events:
            timeline_events.append({
                "date": event.watered_at.date(),
                "plant_name": plant.name,
                "species_name": plant.species.name,
                "type": "watered",
            })

        # Next upcoming watering
        next_date = plant.next_watering.date()
        timeline_events.append({
            "date": next_date,
            "plant_name": plant.name,
            "species_name": plant.species.name,
            "type": "overdue" if next_date <= today else "upcoming",
        })

    # Sort by date
    timeline_events.sort(key=lambda e: e["date"])

    # Group events by date for the calendar view
    from collections import OrderedDict
    days = OrderedDict()
    for event in timeline_events:
        date_key = event["date"]
        if date_key not in days:
            days[date_key] = []
        days[date_key].append(event)

    return render_template("dashboard.html", days=days, today=today)
