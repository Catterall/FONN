from fastapi import FastAPI
from routes.article_routes import router as article_router
from routes.auth_routes import router as auth_router

app = FastAPI()
app.include_router(article_router, prefix="/article", tags=["Article"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
