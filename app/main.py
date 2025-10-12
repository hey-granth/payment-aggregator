from fastapi import FastAPI
from .users.routes import router as users_router


app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "API Payment Aggregator running successfully bishes!"}


app.include_router(users_router)
