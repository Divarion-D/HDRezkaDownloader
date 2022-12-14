from fastapi import FastAPI, Header
import uvicorn
from typing import Union
from hd_rezka_parser import HdRezkaParser
from hd_rezka_api import HdRezkaApi
import enum
import json
import sys

app = FastAPI()

HDREZKA_URL = "http://rd8j1em1zxge.org/"

def custom_openapi():
    with open("openapi.json", "r") as openapi:
        return json.load(openapi)

app.openapi = custom_openapi


@app.get("/content/search/")
async def search(query: str, page: int = 1):
    mirror = HDREZKA_URL
    search_url: str = f"{mirror}search/?do=search&subaction=search&q={query}&page={page}"
    parser: HdRezkaParser = HdRezkaParser(search_url)
    return parser.get_content_list(mirror)


@app.get("/content/details/")
async def get_concrete(url: Union[str, None] = None, id: Union[int, None] = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        return HdRezkaParser.get_concrete_content_info(url)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        return HdRezkaParser.get_concrete_content_info(url)
    else:
        return {"error": "url and id cannot be used together"}


@app.get("/content/translations/")
async def get_content_translations(url: Union[str, None] = None, id: Union[int, None] = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    return api.getTranslations()


@app.get("/content/movie/videos/")
async def get_movie_videos(url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    stream = api.getStream(translation=translation_id)
    return stream.videos


@app.get("/content/tv_series/seasons/")
async def get_tv_series_seasons(url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    if url is None and id is None:
        return {"error": "url or id is required"}
    elif url is not None and id is None:
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    elif url is None and id is not None:
        url = HdRezkaParser.get_url_by_id(HDREZKA_URL, id)
        api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    else:
        return {"error": "url and id cannot be used together"}

    return api.getSeasons(translator_id=translation_id)


@app.get("/content/tv_series/videos/")
async def get_tv_series_videos(season_id: str, episode_id: str, url: Union[str, None] = None, id: Union[int, None] = None, translation_id: str = None):
    api: HdRezkaApi = HdRezkaApi(url, HDREZKA_URL)
    stream = api.getStream(translation=translation_id,
                           season=season_id, episode=episode_id)
    return stream.videos


@app.get("/content/page/{page}")
async def get_content(page: int, filter: str = "last", type: str = "all"):
    mirror = HDREZKA_URL
    url: str = create_url(page, filter, type, mirror)
    print(url)
    parser: HdRezkaParser = HdRezkaParser(url)
    return parser.get_content_list(mirror)



@app.get("/content/category/page/{page}")
async def get_content_by_categories(page: int = 1, type: str = "films", genre: str = "any", year: int = None):
    mirror = HDREZKA_URL
    url = create_categories_url(page, type, genre, year, mirror)
    parser: HdRezkaParser = HdRezkaParser(url)
    return parser.get_content_list(mirror)


def create_url(page: int, filter: str, type: str, mirror: str):
    genre_index: int = ContentType[f"{type}"].value
    url = mirror
    if(page != 1):
        url += f"/page/{page}/"
    url += f"?filter={filter}"
    if genre_index != 0:
        url = f"{url}&genre={genre_index}"
    return url


def create_categories_url(page: int, type: str, genre: str, year: int, mirror: str):
    url = f"{mirror}{type}/best/"
    if genre != "any":
        url += f"{genre}/"
    if year != None:
        url += f"{year}/"
    if page != 1:
        url += f"page/{page}/"
    return url


class ContentType(enum.Enum):
    all = 0
    film = 1
    series = 2
    cartoon = 3
    anime = 82


if __name__ == "__main__":
    ip = input("Enter ip (default: 127.0.1.1): ")
    port = input("Enter port (default: 8000): ")
    if ip == "":
        ip = "127.0.1.1"
    if port == "":
        port = "8000"
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
