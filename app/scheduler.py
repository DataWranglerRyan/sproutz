from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message

from app import db, mail
from app.models import Plant


def check_reminders(app):
    """Check for plants that need watering and send email reminders."""
    with app.app_context():
        overdue_plants = [p for p in Plant.query.all() if p.is_overdue]

        if not overdue_plants and not app.config.get("REMINDER_EMAIL"):
            return

        if overdue_plants and app.config.get("REMINDER_EMAIL"):
            plant_list = "\n".join(
                f"- {p.name} ({p.species.name}): overdue by {abs(p.days_until_watering)} day(s)"
                for p in overdue_plants
            )
            msg = Message(
                subject=f"🌱 {len(overdue_plants)} plant(s) need watering!",
                recipients=[app.config["REMINDER_EMAIL"]],
                body=f"The following plants are overdue for watering:\n\n{plant_list}",
            )
            try:
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Failed to send reminder email: {e}")


def start_scheduler(app):
    """Start the background scheduler to check reminders daily."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=check_reminders,
        args=[app],
        trigger="interval",
        hours=24,
        id="water_reminder",
    )
    scheduler.start()
