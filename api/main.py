from fastapi import FastAPI
from api.routers import line

app = FastAPI()
app.include_router(line.router)

@app.get("/hello")
async def hello():
    return {"message": "hello world!"}
