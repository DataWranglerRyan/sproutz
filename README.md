# Sproutz

## Single-user login setup

1. Install dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

2. Copy `.env.example` to `.env`.
3. Generate a session secret:

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. Generate a password hash, replacing the sample password:

   ```bash
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('choose-a-strong-password', method='pbkdf2:sha256'))"
   ```

5. Set `SECRET_KEY`, `AUTH_USERNAME`, and `AUTH_PASSWORD_HASH` in `.env`, then run:

   ```bash
   python3 run.py
   ```

Set `SESSION_COOKIE_SECURE=true` when serving the app over HTTPS. Do not commit `.env`.

## Deploying to Render

1. Commit and push this project to GitHub. Do not commit `.env` or `plants.db`.
2. In Render, choose **New** → **Blueprint** and select the repository. Render reads
   `render.yaml` and creates the Python web service.
3. Enter `AUTH_USERNAME` and `AUTH_PASSWORD_HASH` when Render asks for the values.
4. In the web service's **Environment** settings, set `DATABASE_URL` to the
   **Internal Database URL** of your existing Render PostgreSQL database.
5. Deploy. The health check is served at `/login`.
6. After the first deploy, use the Render Shell to load the standard species:

   ```bash
   python seed.py
   ```

`db.create_all()` creates the empty database schema at startup. Existing data in
the local SQLite `plants.db` is not copied automatically.
