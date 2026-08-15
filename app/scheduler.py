import urllib.request

from apscheduler.schedulers.background import BackgroundScheduler

from app.models import Plant


def send_ntfy_notification(app, title, message):
    """Send a push notification via ntfy.sh."""
    topic = app.config.get("NTFY_TOPIC")
    if not topic:
        return

    server = app.config.get("NTFY_SERVER", "https://ntfy.sh")
    url = f"{server.rstrip('/')}/{topic}"
    # HTTP headers must be Latin-1; strip anything outside that range
    # (e.g. emoji) rather than let the request fail to encode.
    safe_title = title.encode("latin-1", "ignore").decode("latin-1")
    req = urllib.request.Request(
        url,
        data=message.encode("utf-8"),
        headers={
            "Title": safe_title,
            "Priority": "default",
            "Tags": "seedling",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        app.logger.error(f"Failed to send ntfy reminder: {e}")


def check_reminders(app):
    """Check for plants that need watering and send a push reminder via ntfy.sh."""
    with app.app_context():
        overdue_plants = [p for p in Plant.query.all() if p.is_overdue]

        if not overdue_plants:
            return

        plant_list = "\n".join(
            f"- {p.name} ({p.species.name}): overdue by {abs(p.days_until_watering)} day(s)"
            for p in overdue_plants
        )
        send_ntfy_notification(
            app,
            title=f"{len(overdue_plants)} plant(s) need watering!",
            message=f"The following plants are overdue for watering:\n\n{plant_list}",
        )


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
