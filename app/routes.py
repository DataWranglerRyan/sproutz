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
    import calendar as cal
    from collections import OrderedDict

    plants = Plant.query.all()
    today = datetime.utcnow().date()

    # Get month/year from query params for navigation
    try:
        year = int(request.args.get("year", today.year))
        month = int(request.args.get("month", today.month))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    # Clamp month and adjust year
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Build timeline: past watering events + future scheduled waterings
    timeline_events = []
    watering_dates = {}

    for plant in plants:
        for event in plant.watering_events:
            timeline_events.append({
                "date": event.watered_at.date(),
                "plant_name": plant.name,
                "species_name": plant.species.name,
                "type": "watered",
            })

        next_date = plant.next_watering.date()
        event_type = "overdue" if next_date <= today else "upcoming"
        timeline_events.append({
            "date": next_date,
            "plant_name": plant.name,
            "species_name": plant.species.name,
            "type": event_type,
        })

        if next_date not in watering_dates:
            watering_dates[next_date] = []
        watering_dates[next_date].append({
            "name": plant.name,
            "overdue": next_date <= today,
        })

    timeline_events.sort(key=lambda e: e["date"])

    days = OrderedDict()
    for event in timeline_events:
        date_key = event["date"]
        if date_key not in days:
            days[date_key] = []
        days[date_key].append(event)

    # Build calendar data for selected month
    from datetime import date
    month_name = date(year, month, 1).strftime("%B %Y")
    first_weekday, num_days = cal.monthrange(year, month)
    first_weekday = (first_weekday + 1) % 7  # Adjust to Sunday=0

    calendar_days = []
    for _ in range(first_weekday):
        calendar_days.append(None)
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        calendar_days.append({
            "day": day,
            "date": d,
            "is_today": d == today,
            "has_watering": d in watering_dates,
            "is_overdue": d in watering_dates and any(p["overdue"] for p in watering_dates[d]),
            "plants": watering_dates.get(d, []),
        })

    # Prev/next month links
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    return render_template(
        "dashboard.html",
        days=days,
        today=today,
        calendar_days=calendar_days,
        month_name=month_name,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        current_year=today.year,
        current_month=today.month,
    )
