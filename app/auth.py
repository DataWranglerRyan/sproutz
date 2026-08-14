from urllib.parse import urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import UserMixin, current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from app import login_manager

auth = Blueprint("auth", __name__)


class SingleUser(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(user_id):
    username = current_app.config["AUTH_USERNAME"]
    if user_id == username:
        return SingleUser(username)
    return None


def is_safe_next_url(next_url):
    if not next_url:
        return False
    parsed_url = urlparse(next_url)
    return not parsed_url.scheme and not parsed_url.netloc and next_url.startswith("/")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    next_url = request.values.get("next")
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if (
            username == current_app.config["AUTH_USERNAME"]
            and check_password_hash(current_app.config["AUTH_PASSWORD_HASH"], password)
        ):
            login_user(SingleUser(username))
            return redirect(
                next_url if is_safe_next_url(next_url) else url_for("main.dashboard")
            )
        flash("Invalid username or password.", "info")

    return render_template("login.html", next_url=next_url)


@auth.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
