from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from utils import get_mongo_client
from routes import router

logging.getLogger().setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app:FastAPI):
    app.mongodb_client = get_mongo_client()
    app.mongodb_database = app.mongodb_client.get_database("readbooks")
    logging.info("Connected to MongoDB!")
    yield
    app.mongodb_client.close()
    logging.info("Connection to MongoDB closed.")




app = FastAPI(lifespan=lifespan)

app.include_router(router, tags=["books"], prefix="/book")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8080)