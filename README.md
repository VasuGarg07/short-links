# Short Links

Paste a long link, get a short one. Opening the short link sends you to the long one and
counts the click.

## Run it

You need Docker Desktop installed and open (wait until it says it is running).

1. Download the project and go into its folder:

   ```
   git clone <this repo's URL>
   cd short-links
   ```

2. Create your settings file. It holds the database password, and it stays on your
   computer (it is never uploaded to GitHub). Copy the example file:

   Windows:

   ```
   copy .env.example .env
   ```

   Mac or Linux:

   ```
   cp .env.example .env
   ```

   Open the new `.env` file and change `DB_PASSWORD=change-me` to a password you choose.
   Use only letters and numbers.

3. Start everything:

   ```
   docker compose up --build
   ```

   The first run takes a few minutes because Docker downloads and builds things. It is
   ready when the log stops scrolling and you see `Application startup complete`.

4. Open http://localhost:3000 in your browser.

## Stop it

Press `Ctrl+C` in the terminal where it is running, then run:

```
docker compose down
```

Your links are kept. To delete all links and start fresh, run `docker compose down -v`.

## If something goes wrong

- `DB_PASSWORD` is missing: you skipped step 2. Create the `.env` file and run step 3 again.
- `password authentication failed`: you changed the password after the first start. Run
  `docker compose down -v` (this deletes your links) and start again.
- `port is already allocated`: another program uses port 3000, 8000 or 5432. Close it and
  run the command again.
- `Cannot connect to the Docker daemon`: Docker Desktop is not running. Open it and wait.

## What is inside

- `frontend/`: the web page (React), served by nginx on port 3000.
- `backend/`: the API (Python, FastAPI) on port 8000. Short links open here.
- `backend/migrations/`: the SQL that creates the database table. Postgres runs it on the
  first start.
- `docker-compose.yml`: starts the database, backend and frontend together.
