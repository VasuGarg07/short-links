# Short Links: Journal

A URL shortener built as a learning project: create a short link, redirect to the long
URL, count clicks. Stack: Python, FastAPI, Postgres (Docker), pytest.

This is a dev diary, newest entries at the bottom. One or two paragraphs each. Entries
that record a choice start with "Decision:" and name the option I rejected.

## 2026-10-13: Kickoff
Decision: Python + FastAPI for the backend, TypeScript + React for the frontend. Rejected
TypeScript + NestJS: it is new to me and heavy on boilerplate, and this project is about
backend concepts (DB, transactions, concurrency, Docker, CI), which are language-independent.
I already know Flask, so FastAPI is a small step. Cost: no shared types between backend and
frontend, and I need to learn Python's async model and the GIL, which is useful interview
material. Tooling: uv, uvicorn, psycopg (raw SQL), pytest, ruff, mypy, each added only when
needed.

Checked my machine: Node 24, Python 3.14, uv, Postgres 18, git are installed. Docker is not;
I need it by step 6. The project uses Python 3.13 for library compatibility. Debugging works
in VS Code via F5 with uvicorn. One git repo for backend and frontend (backend in `backend/`).

## 2026-10-13: Step 2 data structure
Decision: in-memory list of records instead of a dict, because it maps closer to rows in a
table. Tradeoff: lookup by code is a full scan (like a DB with no index) and unique codes
must be checked by hand. Step 3 fixes both with a UNIQUE index on `slug`.

## 2026-10-14: Steps 1 and 2 done, 301 vs 302
Finished setup and the three endpoints (create, redirect, stats) on an in-memory list.
Learned the difference between the two redirect codes. 301 means moved permanently: browsers
cache it heavily, so it suits a URL that will never point elsewhere. 302 means moved
temporarily: the browser is not told to remember it, so every click comes back to my server.
A URL shortener uses 302 so every click can be counted, and so the target behind a slug can
be changed later.

## 2026-10-14: Postgres in Docker (inside WSL2) instead of a local install
Decision: run Postgres 18 in a Docker container, with Docker Engine installed inside an
Ubuntu 24.04 WSL2 distro, instead of the Windows Postgres install or Docker Desktop. The
local install was broken: `CREATE DATABASE` failed with a block-read "Invalid argument" error
and a plain `SHOW` crashed the backend. I did not find the root cause and did not want to
spend hours on it. Docker Desktop was rejected as heavier on RAM and always running; Docker in
WSL2 only runs when I open it, and `wsl --shutdown` frees everything. Ubuntu lives on D:
(`wsl --install --location`) because C: is nearly full. Cost: more setup and some Linux
commands to learn.

Compose file: image pinned to `postgres:18`, password read from `.env` (gitignored, with a
`.env.example`), port published only on `127.0.0.1` so it is not exposed to the network, data
in a named volume mounted at `/var/lib/postgresql` (the path changed in Postgres 18).
Learned: image vs container, port mapping `host:container`, why a volume is needed, YAML
indentation, and that `docker compose down -v` deletes the data.

## 2026-10-14: Step 3 done, Postgres behind the API
Wrote `001_create_links.sql` by hand (identity id, unique slug, `TIMESTAMPTZ`) and moved all
three endpoints from the list to psycopg with parameterized queries. Bugs I hit: a 500 from
`clicks=[3]` (a list instead of an int), which also rolled back the insert because an
exception inside `with conn` means rollback; `row[1]` on a one-column `SELECT`; and returning
the numeric id as the slug. Also learned that FastAPI checks the response against the return
type, and pydantic turned `id=1` into `true` for `str | bool`.

Decision: handle slug collisions with `INSERT ... ON CONFLICT DO NOTHING RETURNING slug` in
a loop of at most 5 attempts, instead of catching `UniqueViolation` (which leaves the
transaction in an error state) or checking first (which races). Decision: skip the `UNIQUE`
index on `url` for now, with a known limitation: the "does this URL already exist" lookup
scans every row and two simultaneous posts of one URL can both insert. Fixed in step 4 with
migration `002`. Core lesson: check-then-act breaks under concurrency, so let the database
enforce it with a constraint or an atomic statement like `clicks = clicks + 1`.

## 2026-10-16: Steps 4 and 5 done, tests and error handling
Added migration `002` (`UNIQUE` on `url`) and reworked `create_link` to insert first and look
up the existing slug only if the insert did nothing, so two simultaneous posts of one URL
cannot both insert. Added pytest with a separate `short_links_test` database. A guard in
`conftest.py` refuses to run unless the database name ends in `_test`, and each test starts
from an empty table. Two tests: same URL twice gives the same slug, and 50 parallel clicks on
one slug give exactly 50 clicks. Lesson: a transaction alone does not fix a lost update at
the default isolation level, the single atomic `UPDATE` does.

Decision: step 5 is validation in code plus a few error cases, not more tests. Bad URLs
return 422 (pydantic `HttpUrl`), unknown slugs 404, and a database outage 503 instead of 500.
Rejected: more trivial tests, since the manual checks in earlier steps already covered them.
I also tried a slug-pattern check (malformed slug -> 422) and then dropped it, so a malformed
slug now falls through to the normal 404. Known gaps: no automated test for parallel posts of
one URL or a forced slug collision (both checked by hand), and one new connection per request,
no pool.


## 2026-10-16: Frontend added, code style rule
Added `frontend/`: a React + TypeScript + Vite page that shortens a link, lists my links with
click counts, and copies the short URL. Only `fetch`, no router, state library or CSS
framework. Vite forwards `/links` to FastAPI, so the browser talks to one origin and the
backend needs no CORS setup. VS Code can debug the backend and the page together.

## 2026-10-16: One-command start with Docker Compose
Decision: `docker compose up --build` starts the whole app for someone who only cloned the repo.
Three services: Postgres, the FastAPI backend, and the frontend (built, then served by nginx,
which also forwards `/links` to the backend). The migration files are mounted into Postgres'
init folder, so the table is created automatically on the first start. The backend waits for a
Postgres health check, which uses TCP because Postgres also answers on a local socket while it
is still running the init scripts. Decision: newcomers must create a `.env` file from
`.env.example` (README step 2). Rejected: a local-only default password in the compose file,
since it skips a good habit and puts a password in the repo. Compose now stops with a clear
message if `DB_PASSWORD` is missing. Cost: one extra setup step, and migrations only run on an
empty database, so a later migration needs `docker compose down -v` or a manual run. Written
but not yet run end to end.
