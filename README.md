# OpenPath-RPI
An accessible campus navigation app for finding routes based on usersâ€™ mobility and accessibility needs.

## Run locally

The frontend gets map and route data from Django, so `npm run dev` by itself
does not start the whole app. Choose one of these options:

### Docker Compose

Start Docker Desktop, then run from the repository root:

```sh
docker compose up --build
```

Open <http://localhost:5173>. Compose starts PostgreSQL and Django before Vite.

### Frontend and Django separately

In one terminal, install the backend requirements and start Django (SQLite is
used when `POSTGRES_HOST` is not set):

```sh
cd backend
python -m venv .venv
```

On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1` (on
macOS/Linux, use `source .venv/bin/activate`), then run:

```sh
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

In a second terminal:

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` requests to Django on port
8000; if Django is stopped, the page explains how to start the API and offers
a retry.

## Map data

The campus location and path data format is documented in
[data/README.md](data/README.md). Django and Docker read the shared files in
`data/`. Set `OPENPATH_DATA_DIR` to use another directory containing both
`locations.json` and `paths.json`. The copies in `backend/locations/` are
retained as historical snapshots.

The dataset is provisional and many paths have not been recorded. A missing
route needs observed path data; do not invent connections or mark real
locations as mock to silence validation errors.

## Checks

From `backend/`, with its virtual environment active:

```sh
pip install -r requirements-dev.txt
python manage.py test
python -m unittest locations.conceptual_tests
ruff check .
ruff format --check .
python -m locations.validate_graph
```

The validator currently reports missing campus connections.

From `frontend/`, use Node 22.22.2+, Node 24.15+, or Node 26+:

```sh
npm ci
npm run lint
npm test -- --run
npm run build
```

The historical Excel audit is separate from the route API. To run it, install
`backend/requirements-pathfinding.txt`, then run `python -m pathfinding.main`
from `backend/`. It exits unsuccessfully when landmarks remain disconnected.

## Deployment settings

Compose and Django runserver are for development. A production deployment
needs a production application server and HTTPS. Set `DJANGO_DEBUG=false`, a
random `DJANGO_SECRET_KEY`, and comma-separated `DJANGO_ALLOWED_HOSTS`. Set
`DJANGO_CORS_ORIGINS` for any separate frontend origin. Django refuses to start
in non-debug mode without a secret. `.env.example` lists Compose defaults;
set environment variables in your shell when starting Django manually.

# Instructions:
1. Choose or receive a GitHub issue.
2. Create a branch for that issue.
3. Make and test your changes.
4. Commit your work using a clear message.
5. Push the branch to GitHub.
6. Open a pull request.
7. Do not merge your own pull request unless the Project Lead approves it.
