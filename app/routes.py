from flask import Blueprint, Response, render_template, request, redirect, url_for, flash
from flask_login import current_user
from datetime import datetime, timedelta

from app import db
from app.models import (
    CENTRAL_TZ,
    Plant,
    Species,
    SpeciesIssue,
    WateringEvent,
    to_central,
)
from app.storage import (
    PlantPhotoError,
    delete_plant_photo,
    download_plant_photo,
    upload_plant_photo,
)

main = Blueprint("main", __name__)


@main.before_request
def require_login():
    if request.endpoint == "main.health":
        return
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login", next=request.full_path))


@main.route("/health")
def health():
    """Lightweight, unauthenticated endpoint for uptime pingers to keep the app awake."""
    return "OK", 200


@main.route("/")
def home():
    return redirect(url_for("main.dashboard"))


@main.route("/plants")
def index():
    all_plants = Plant.query.order_by(Plant.name.asc()).all()
    selected_species_id = request.args.get("species_id", type=int)
    species_plants = [
        plant
        for plant in all_plants
        if selected_species_id is None or plant.species_id == selected_species_id
    ]
    available_locations = sorted(
        {plant.location for plant in species_plants if plant.location}
    )
    selected_location = request.args.get("location", "").strip() or None
    plants = [
        plant
        for plant in species_plants
        if selected_location is None or plant.location == selected_location
    ]
    plants_sorted = sorted(plants, key=lambda p: p.next_watering)
    species = Species.query.order_by(Species.name.asc()).all()
    filter_species = sorted(
        {plant.species_id: plant.species for plant in all_plants}.values(),
        key=lambda item: item.name,
    )
    undoable_plant_ids = set()
    for plant in plants:
        active_events = [event for event in plant.watering_events if not event.is_reverted]
        latest_event = max(
            active_events,
            key=lambda event: (event.watered_at, event.id),
            default=None,
        )
        if latest_event and latest_event.previous_last_watered is not None:
            undoable_plant_ids.add(plant.id)
    return render_template(
        "index.html",
        plants=plants_sorted,
        species=species,
        filter_species=filter_species,
        available_locations=available_locations,
        selected_species_id=selected_species_id,
        selected_location=selected_location,
        undoable_plant_ids=undoable_plant_ids,
    )


@main.route("/plants/add", methods=["GET", "POST"])
def add_plant():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        species_id = request.form["species_id"]
        species = Species.query.get_or_404(species_id)

        if not location:
            flash("Location is required.", "info")
            return redirect(request.referrer or url_for("main.add_plant"))

        plant_name = name or f"{location} {species.name}"
        plant = Plant(name=plant_name, location=location, species_id=species.id)
        db.session.add(plant)
        db.session.flush()

        photo = request.files.get("photo")
        if photo and photo.filename:
            try:
                plant.photo_blob_name = upload_plant_photo(plant.id, photo)
            except PlantPhotoError as error:
                db.session.rollback()
                flash(str(error), "info")
                return redirect(request.referrer or url_for("main.add_plant"))

        db.session.commit()
        flash(f"Added {plant_name}!", "success")
        return redirect(url_for("main.index"))
    species = Species.query.all()
    return render_template("add_plant.html", species=species)


@main.route("/plants/<int:plant_id>/water", methods=["POST"])
def water_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    previous_last_watered = plant.last_watered
    previous_snoozed_until = plant.snoozed_until
    plant.water()
    event = WateringEvent(
        plant_id=plant.id,
        watered_at=datetime.utcnow(),
        previous_last_watered=previous_last_watered,
        previous_snoozed_until=previous_snoozed_until,
    )
    db.session.add(event)
    db.session.commit()
    flash(f"Watered {plant.name}!", "success")
    return redirect(request.referrer or url_for("main.index"))


@main.route("/plants/<int:plant_id>/water/undo", methods=["POST"])
def undo_water_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    event = (
        WateringEvent.query.filter_by(plant_id=plant.id, is_reverted=False)
        .order_by(WateringEvent.watered_at.desc(), WateringEvent.id.desc())
        .first()
    )
    if event is None:
        flash(f"No watering event to undo for {plant.name}.", "info")
        return redirect(request.referrer or url_for("main.index"))
    if event.previous_last_watered is None:
        flash("This watering event cannot be undone because it predates undo tracking.", "info")
        return redirect(request.referrer or url_for("main.index"))

    event.is_reverted = True
    event.reverted_at = datetime.utcnow()
    plant.last_watered = event.previous_last_watered
    plant.snoozed_until = event.previous_snoozed_until
    db.session.commit()
    flash(f"Undid last watering for {plant.name}.", "success")
    return redirect(request.referrer or url_for("main.index"))


@main.route("/plants/<int:plant_id>/delete", methods=["POST"])
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if plant.photo_blob_name:
        try:
            delete_plant_photo(plant.photo_blob_name)
        except PlantPhotoError as error:
            flash(str(error), "info")
            return redirect(request.referrer or url_for("main.index"))
    db.session.delete(plant)
    db.session.commit()
    flash(f"Removed {plant.name}.", "info")
    return redirect(url_for("main.index"))


@main.route("/plants/<int:plant_id>/photo", methods=["GET", "POST"])
def plant_photo(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if request.method == "POST":
        try:
            plant.photo_blob_name = upload_plant_photo(
                plant.id, request.files.get("photo")
            )
        except PlantPhotoError as error:
            flash(str(error), "info")
            return redirect(request.referrer or url_for("main.index"))

        db.session.commit()
        flash(f"Updated {plant.name}'s photo.", "success")
        return redirect(request.referrer or url_for("main.index"))

    if not plant.photo_blob_name:
        return "Photo not found.", 404
    try:
        photo, content_type = download_plant_photo(plant.photo_blob_name)
    except PlantPhotoError:
        return "Photo not found.", 404

    response = Response(photo, content_type=content_type)
    response.headers["Cache-Control"] = "private, max-age=3600"
    return response


@main.route("/plants/<int:plant_id>/photo/delete", methods=["POST"])
def delete_plant_photo_route(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if not plant.photo_blob_name:
        flash(f"{plant.name} does not have a photo to remove.", "info")
        return redirect(request.referrer or url_for("main.index"))

    try:
        delete_plant_photo(plant.photo_blob_name)
    except PlantPhotoError as error:
        flash(str(error), "info")
        return redirect(request.referrer or url_for("main.index"))

    plant.photo_blob_name = None
    db.session.commit()
    flash(f"Removed {plant.name}'s photo.", "success")
    return redirect(request.referrer or url_for("main.index"))


@main.route("/plants/<int:plant_id>/snooze", methods=["POST"])
def snooze_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    try:
        days = int(request.form.get("days", "0"))
    except ValueError:
        days = 0

    if days < 1:
        flash("Snooze days must be at least 1.", "info")
        return redirect(request.referrer or url_for("main.index"))

    plant.snooze(days)
    db.session.commit()
    flash(f"Snoozed {plant.name} for {days} day(s).", "success")
    return redirect(request.referrer or url_for("main.index"))


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
    return render_template("species_detail.html", species=species, edit_mode=False)


@main.route("/species/<int:species_id>/edit", methods=["GET", "POST"])
def edit_species(species_id):
    species = Species.query.get_or_404(species_id)
    if request.method == "POST":
        section = request.form.get("section")
        if section == "general":
            species.watering_interval_days = int(request.form["watering_interval_days"])
            species.sunlight = request.form.get("sunlight", "").strip()
            species.soil_type = request.form.get("soil_type", "").strip()
            species.care_tips = request.form.get("care_tips", "").strip()
        elif section == "fertilizer":
            species.fertilizer_type = request.form.get("fertilizer_type", "").strip()
            species.fertilizer_schedule = request.form.get("fertilizer_schedule", "").strip()
            species.fertilizer_notes = request.form.get("fertilizer_notes", "").strip()
        elif section == "issues":
            SpeciesIssue.query.filter_by(species_id=species.id).delete()
            issues = request.form.getlist("issue[]")
            solutions = request.form.getlist("solution[]")
            for issue, solution in zip(issues, solutions):
                if issue.strip() and solution.strip():
                    db.session.add(SpeciesIssue(
                        species_id=species.id,
                        issue=issue.strip(),
                        solution=solution.strip(),
                    ))
        else:
            species.name = request.form["name"].strip()
            species.watering_interval_days = int(request.form["watering_interval_days"])
            species.sunlight = request.form.get("sunlight", "").strip()
            species.soil_type = request.form.get("soil_type", "").strip()
            species.common_issues = request.form.get("common_issues", "").strip()
            species.care_tips = request.form.get("care_tips", "").strip()
            species.fertilizer_type = request.form.get("fertilizer_type", "").strip()
            species.fertilizer_schedule = request.form.get("fertilizer_schedule", "").strip()
            species.fertilizer_notes = request.form.get("fertilizer_notes", "").strip()

            SpeciesIssue.query.filter_by(species_id=species.id).delete()
            issues = request.form.getlist("issue[]")
            solutions = request.form.getlist("solution[]")
            for issue, solution in zip(issues, solutions):
                if issue.strip() and solution.strip():
                    db.session.add(SpeciesIssue(
                        species_id=species.id,
                        issue=issue.strip(),
                        solution=solution.strip(),
                    ))

        db.session.commit()
        flash(f"Updated species: {species.name}", "success")
        return redirect(url_for("main.species_detail", species_id=species.id))

    return render_template("species_detail.html", species=species, edit_mode=True)


@main.route("/dashboard")
def dashboard():
    import calendar as cal
    from collections import OrderedDict

    all_plants = Plant.query.order_by(Plant.name.asc()).all()
    selected_species_id = request.args.get("species_id", type=int)
    all_species = sorted(
        {plant.species_id: plant.species for plant in all_plants}.values(),
        key=lambda species: species.name,
    )
    species_plants = [
        plant
        for plant in all_plants
        if selected_species_id is None or plant.species_id == selected_species_id
    ]
    available_locations = sorted(
        {plant.location for plant in species_plants if plant.location}
    )
    selected_location = request.args.get("location", "").strip() or None
    available_plants = [
        plant
        for plant in species_plants
        if selected_location is None or plant.location == selected_location
    ]
    selected_plant_id = request.args.get("plant_id", type=int)
    selected_plant = next(
        (plant for plant in available_plants if plant.id == selected_plant_id),
        None,
    )
    plants = [selected_plant] if selected_plant else available_plants
    today = datetime.now(CENTRAL_TZ).date()
    tomorrow = today + timedelta(days=1)
    next_up = {"today": [], "tomorrow": []}

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
        photo_url = url_for("main.plant_photo", plant_id=plant.id) if plant.photo_blob_name else None
        active_events = [event for event in plant.watering_events if not event.is_reverted]
        latest_event = max(
            active_events,
            key=lambda event: (event.watered_at, event.id),
            default=None,
        )
        for event in active_events:
            if event.is_reverted:
                continue
            timeline_events.append({
                "date": to_central(event.watered_at).date(),
                "plant_id": plant.id,
                "plant_name": plant.name,
                "species_name": plant.species.name,
                "photo_url": photo_url,
                "type": "watered",
                "undoable": event is latest_event and event.previous_last_watered is not None,
            })

        next_date = to_central(plant.next_watering).date()
        if next_date <= today:
            next_up["today"].append(plant)
        elif next_date == tomorrow:
            next_up["tomorrow"].append(plant)
        event_type = "overdue" if next_date <= today else "upcoming"
        timeline_events.append({
            "date": next_date,
            "plant_id": plant.id,
            "plant_name": plant.name,
            "species_name": plant.species.name,
            "photo_url": photo_url,
            "type": event_type,
        })

        if next_date not in watering_dates:
            watering_dates[next_date] = []
        watering_dates[next_date].append({
            "id": plant.id,
            "name": plant.name,
            "species": plant.species.name,
            "photo_url": photo_url,
            "overdue": next_date <= today,
            "undoable": latest_event is not None and latest_event.previous_last_watered is not None,
        })

    timeline_events.sort(key=lambda e: e["date"])

    days = OrderedDict()
    for event in timeline_events:
        date_key = event["date"]
        if date_key not in days:
            days[date_key] = []
        days[date_key].append(event)
    past_days = OrderedDict(
        (date_key, events)
        for date_key, events in days.items()
        if date_key <= today
    )
    upcoming_days = OrderedDict(
        (date_key, events)
        for date_key, events in days.items()
        if date_key > today
    )

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
        past_days=past_days,
        upcoming_days=upcoming_days,
        today=today,
        calendar_days=calendar_days,
        month_name=month_name,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        current_year=today.year,
        current_month=today.month,
        next_up=next_up,
        all_plants=all_plants,
        all_species=all_species,
        available_plants=available_plants,
        selected_plant_id=selected_plant.id if selected_plant else None,
        selected_species_id=selected_species_id,
        available_locations=available_locations,
        selected_location=selected_location,
    )
