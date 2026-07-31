from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models import Plant, Species

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
        species = Species(name=name, watering_interval_days=interval)
        db.session.add(species)
        db.session.commit()
        flash(f"Added species: {name}", "success")
        return redirect(url_for("main.manage_species"))
    species = Species.query.all()
    return render_template("species.html", species=species)
