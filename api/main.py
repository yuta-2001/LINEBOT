from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routers import line

app = FastAPI()
app.include_router(line.router)

app.mount("/images", StaticFiles(directory="images"), name="images")

@app.get("/hello")
async def hello():
    return {"message": "hello world!"}
