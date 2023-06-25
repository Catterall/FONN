from cachetools import TTLCache, cached
from fastapi import APIRouter, HTTPException, Path, status

from data.database import FONNDB

router = APIRouter()
db = FONNDB()
article_cache = TTLCache(maxsize=100, ttl=3600)  # Articles cached for one hour

@router.get("/preview-list/{page}")
@cached(article_cache)
def get_articles(page: int = Path(title="Page", description="A page of articles: each page contains the next 10 articles")):
    """Returns a list of previews of articles with the author"""
    articles = db.select("""
        SELECT
            ar.[ArticleID],
            ar.[Title],
            ar.[Description],
            ar.[PreviewImage],
            ar.[CreationDate],
            ar.[ModifiedDate],
            au.[AuthorID],
            au.[Forename],
            au.[Surname],
            au.[Avatar]
        FROM
            Article ar
        INNER JOIN
            AuthorArticle aa ON ar.ArticleID = aa.ArticleID
        INNER JOIN
            Author au ON au.AuthorID = aa.AuthorID
        ORDER BY
            ar.ArticleID DESC
        OFFSET (? - 1) * 10 ROWS
        FETCH NEXT 10 ROWS ONLY""", page)
    if len(articles) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return [{
        "article_id": article[0],
        "title": article[1],
        "description": article[2],
        "preview_image": article[3],
        "creation_date": article[4],
        "modification_date": article[5],
        "author": {
            "author_id": article[6],
            "forename": article[7],
            "surname": article[8],
            "avatar": article[9]
        }
    } for article in articles]

@router.get("/id-list")
@cached(article_cache)
def get_article_ids():
    """Returns a list of all article IDs"""
    articles = db.select("SELECT ArticleID FROM Article")
    return [article[0] for article in articles]

@router.get("/{article_id}")
@cached(article_cache)
def get_article(article_id: int = Path(title="Article ID", description="ID of the article you want to view")):
    """Returns an article by ID with the author"""
    article = db.select("""
        SELECT
            ar.[ArticleID],
            ar.[Title],
            ar.[Description],
            ar.[Content],
            ar.[PreviewImage],
            ar.[CreationDate],
            ar.[ModifiedDate],
            au.[AuthorID],
            au.[Forename],
            au.[Surname],
            au.[Avatar]
        FROM
            Article ar
        INNER JOIN
            AuthorArticle aa ON ar.ArticleID = aa.ArticleID
        INNER JOIN
            Author au ON au.AuthorID = aa.AuthorID
        WHERE
            (ar.ArticleID = ?)""", article_id)
    if len(article) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article ID not found")
    return {
        "article_id": article[0][0],
        "title": article[0][1],
        "description": article[0][2],
        "content": article[0][3],
        "preview_image": article[0][4],
        "creation_date": article[0][5],
        "modification_date": article[0][6],
        "author": {
            "author_id": article[0][7],
            "forename": article[0][8],
            "surname": article[0][9],
            "avatar": article[0][10]
        }
    }
