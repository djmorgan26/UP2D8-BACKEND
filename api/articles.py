from fastapi import APIRouter, status, HTTPException, Depends
from dependencies import get_db_client

router = APIRouter()

@router.get("/api/articles", status_code=status.HTTP_200_OK)
async def get_articles(db=Depends(get_db_client)):
    articles_collection = db.articles
    articles = list(articles_collection.find({}, {"_id": 0}))
    return articles

@router.get("/api/articles/{article_id}", status_code=status.HTTP_200_OK)
async def get_article(article_id: str, db=Depends(get_db_client)):
    articles_collection = db.articles
    article = articles_collection.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found.")
    return article
