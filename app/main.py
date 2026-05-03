from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()


templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book=BookModel(
    #     keyword="python",
    #     publisher="bjPublic",
    #     price=1200,
    #     image="me.png"
    #     )

    # print(save_book.model_dump(),flush=True)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"title": "콜렉터 북북"}
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):

    keyword = q
    # (예외처리)
    #  - 검색어가 없다면 사용자에게 검색을 요구 return
    #  - 해당 검색어에 대해 수집된 데이터가 이미 DB에 존재한다면 해당 데이터를 사용자에게 보여준다. return
    # 2. 데이터 수집기로 해당 검색어에 대해 데이터를 수집한다.
    naver_book_scraper = NaverBookScraper()
    books = await naver_book_scraper.search(keyword, 10)
    book_models = []
    for book in books:
        print(book)
        book_model = BookModel(
            keyword=keyword,
            publisher=book["publisher"],
            price=int(book.get("discount") or 0),
            image=book["image"],
        )
        book_models.append(book_model)
    await mongodb.engine.save_all(book_models)
    return templates.TemplateResponse(
        request=request, name="index.html", context={"keyword": q, "books": books}
    )


@app.on_event("startup")
async def on_app_start():
    print("hello server")
    mongodb.connect()
    """before app start"""


@app.on_event("shutdown")
async def on_app_shutdown():
    print("goodbye server")
    mongodb.close()
    """after app shutdown"""
