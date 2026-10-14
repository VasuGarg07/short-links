from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from utils import generate_slug, get_db_conn


class LinkRequest(BaseModel):
    url: HttpUrl

MAX_SLUG_ATTEMPTS = 5

app = FastAPI()


@app.get("/")
def health() -> dict[str, str]:
    return {"message": "hello"}


@app.post("/links", status_code=201)
def create_link(request: LinkRequest, response: Response):
    url = str(request.url)
    with get_db_conn() as conn, conn.cursor() as cursor:
        # Find if url already exists
        cursor.execute("SELECT slug FROM links WHERE url = %s;", (url, ))
        row = cursor.fetchone()
        if row is not None:

            # send existing entry with status_code 200
            response.status_code = 200
            return {"slug": row[0], "message": "Entry already exists"}

        # Create new entry. The slug is random, so it can (rarely) already be taken.
        # ON CONFLICT DO NOTHING makes Postgres skip the insert and return no row
        # instead of raising an error, and then we try again with a new slug.
        for _ in range(MAX_SLUG_ATTEMPTS):
            slug = generate_slug()
            cursor.execute(
                "INSERT INTO links (slug, url) VALUES (%s, %s) ON CONFLICT (slug) DO NOTHING RETURNING slug;",
                (slug, url),
            )
            row = cursor.fetchone()
            if row is not None:
                return {"slug": row[0], "message": "New entry created"}

        raise HTTPException(status_code=500, detail="Could not generate a unique slug")


@app.get("/{slug}")
def redirect_link(slug: str) -> RedirectResponse:
    with get_db_conn() as conn, conn.cursor() as cursor:
        cursor.execute("UPDATE links SET clicks = clicks + 1 WHERE slug = %s RETURNING url;", (slug, ))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Url Not Found")

        return RedirectResponse(url=row[0], status_code=302)
            

@app.get("/links/{slug}/stats")
def get_link_stats(slug: str):
    with get_db_conn() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, url, clicks, created_at FROM links WHERE slug = %s;", (slug, ))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Url Not Found")

        return {"id":row[0], "url":row[1], "clicks":row[2], "created_at":row[3]}
