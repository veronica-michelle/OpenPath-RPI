# OpenPath-RPI
An accessible campus navigation app for finding routes based on users’ mobility and accessibility needs.

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

The app reads the shared `data/locations.json` and `data/paths.json` files.
Their format is documented in [data/README.md](data/README.md). Docker includes
and mounts the same directory. Set `OPENPATH_DATA_DIR` to use another data folder.
The copies in `backend/locations/` remain unchanged.

Routing uses path points and individual entrances. Buildings remain named groups
of doors in the existing JSON format. Path `from` and `to` fields must name
entrance IDs (such as `L02B`) or path-point IDs (such as `N001`). Building IDs
(such as `L02`) are invalid path endpoints; the backend never guesses a door
for them. The validator reports these links, the runtime logs and excludes them,
and the distance calculator reports them without measuring them. Selecting a
different door does not move an edge, and doors in the same building have no
implicit connection.
Requests still select a building and optionally an entrance; omitting the entrance
uses the first listed door. A disconnected selected door returns no route.
The map and route responses preserve their structure; route `nodeIds` identify
the actual doors and path points. Run `python -m locations.validate_graph` from
`backend/` to report missing references and disconnected entrances.

The current path connections are fictional placeholders for development and
have not been verified as real walkways or accessibility information. Many
path points still have no connections. Replace the placeholders with surveyed
data before using the app for navigation.

# Instructions:
1. Choose or receive a GitHub issue.
2. Create a branch for that issue.
3. Make and test your changes.
4. Commit your work using a clear message.
5. Push the branch to GitHub.
6. Open a pull request.
7. Do not merge your own pull request unless the Project Lead approves it.
