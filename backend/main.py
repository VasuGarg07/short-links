from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from utils import generate_slug


class LinkRequest(BaseModel):
    url: HttpUrl


class LinkResponse(BaseModel):
    url: HttpUrl
    slug: str
    clicks: int


app = FastAPI()

# MOCK DB: in-memory list of LinkResponse records
links_list: list[LinkResponse] = []


@app.get("/")
def health() -> dict[str, str]:
    return {"message": "hello"}


@app.post("/links", status_code=201)
def create_link(request: LinkRequest, response: Response) -> dict[str, str | bool]:
    for item in links_list:
        if item.url == request.url:
            response.status_code = 200
            return {"slug": item.slug, "message": "Entry already exists"}

    slug = generate_slug()
    links_list.append(LinkResponse(url=request.url, slug=slug, clicks=0))

    return {"slug": slug, "message": "URL saved in DB"}


@app.get("/{slug}")
def redirect_link(slug: str) -> RedirectResponse:
    for item in links_list:
        if item.slug == slug:
            item.clicks += 1
            return RedirectResponse(url=item.url, status_code=302)

    raise HTTPException(status_code=404, detail="Url Not Found")


@app.get("/links/{slug}/stats")
def get_link_stats(slug: str) -> LinkResponse:
    for item in links_list:
        if item.slug == slug:
            return item

    raise HTTPException(status_code=404, detail="Url Not Found")
