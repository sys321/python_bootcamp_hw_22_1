from fastapi import FastAPI
from routes import router
from constants import API_PORT
import uvicorn

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run('main:app', host = '0.0.0.0', port = int(API_PORT), reload = True)